"""
Darwinbox ATS scraper.
Darwinbox is widely used by Indian companies (MPL, Magicpin, Netmeds, Vedantu, etc.)
Uses the public careers page with multiple parsing strategies.
"""

import re
import json
from typing import List, Dict
from .base_scraper import BaseBoardScraper


class DarwinboxScraper(BaseBoardScraper):
    """Scraper for Darwinbox ATS career pages"""

    def __init__(self, rate_limit_ms: int = 2000):
        super().__init__(rate_limit_ms)

    def _extract_slug(self, url: str) -> str:
        """Extract company slug from Darwinbox URL"""
        match = re.search(r'([^/]+)\.darwinbox\.in', url)
        if match:
            return match.group(1)
        return url.rstrip('/').split('/')[-1]

    def scrape_company(self, company_url: str, company_name: str) -> List[Dict]:
        """Scrape jobs from a Darwinbox careers page"""
        slug = self._extract_slug(company_url)
        print(f"  [Darwinbox] Fetching jobs for '{company_name}' (slug: {slug})")

        # Try multiple Darwinbox URL patterns
        urls_to_try = [
            f"https://{slug}.darwinbox.in/ms/candidate/careers",
            f"https://{slug}.darwinbox.in/ms/candidate/careers/a",
            f"https://{slug}.darwinbox.in/career-page",
            company_url,
        ]

        for url in urls_to_try:
            try:
                response = self._safe_get(url)
                if not response or response.status_code != 200:
                    continue

                html = response.text

                # Strategy 1: Look for embedded JSON data in script tags
                jobs = self._extract_from_json_state(html, company_name, slug)
                if jobs:
                    return jobs

                # Strategy 2: Parse HTML for job listings
                jobs = self._parse_html_careers(html, company_name, url)
                if jobs:
                    return jobs

            except Exception as e:
                continue

        print(f"  [Darwinbox] No jobs found for {company_name}")
        self._rate_limit()
        return []

    def _extract_from_json_state(self, html: str, company_name: str, slug: str) -> List[Dict]:
        """Extract jobs from embedded JSON state (Darwinbox embeds data in script tags)"""
        jobs = []

        # Look for JSON data in script tags
        patterns = [
            r'window\.__INITIAL_STATE__\s*=\s*({.*?})\s*;',
            r'window\.__NUXT__\s*=\s*({.*?})\s*;',
            r'"jobs"\s*:\s*(\[.*?\])',
            r'"openings"\s*:\s*(\[.*?\])',
            r'"positions"\s*:\s*(\[.*?\])',
        ]

        for pattern in patterns:
            match = re.search(pattern, html, re.DOTALL)
            if match:
                try:
                    data = json.loads(match.group(1))
                    if isinstance(data, list):
                        for item in data:
                            if isinstance(item, dict) and (item.get('title') or item.get('job_title')):
                                raw = {
                                    'id': str(item.get('id', '')),
                                    'title': item.get('title', item.get('job_title', '')),
                                    'company': company_name,
                                    'location': item.get('location', item.get('city', 'India')),
                                    'url': item.get('url', f"https://{slug}.darwinbox.in/ms/candidate/careers"),
                                    'description': (item.get('description', '') or '')[:500],
                                    'posted_date': item.get('posted_date', item.get('created_at', '')),
                                    'department': item.get('department', ''),
                                }
                                jobs.append(self._normalize_job(raw, source='darwinbox', ats='darwinbox', company_name=company_name))
                except (json.JSONDecodeError, TypeError):
                    continue

        if jobs:
            print(f"  [Darwinbox] Found {len(jobs)} jobs (JSON state) for {company_name}")
        return jobs

    def _parse_html_careers(self, html: str, company_name: str, base_url: str) -> List[Dict]:
        """Parse Darwinbox HTML career page for job listings"""
        jobs = []
        try:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html, 'html.parser')

            # Look for common job listing patterns in Darwinbox pages
            job_selectors = [
                '.job-card', '.career-item', '.job-listing',
                '[class*="job"]', '[class*="career"]', '[class*="opening"]',
                '[class*="position"]', '[class*="vacancy"]',
                'div[class*="listing"]', 'div[class*="role"]',
                'a[href*="job"]', 'a[href*="career"]', 'a[href*="opening"]',
            ]

            cards = []
            for selector in job_selectors:
                found = soup.select(selector)
                if len(found) >= 2:
                    cards = found
                    break

            # Fallback: look for links with job-like patterns
            if not cards:
                all_links = soup.find_all('a', href=True)
                cards = [l for l in all_links if
                         any(kw in l.get('href', '').lower() for kw in ['/job', '/career', '/opening', '/position']) and
                         l.get_text(strip=True) and len(l.get_text(strip=True)) > 5]

            seen = set()
            for card in cards[:100]:
                title = ''
                location = 'India'
                url = base_url

                if card.name == 'a':
                    title = card.get_text(strip=True)
                    url = card.get('href', '')
                else:
                    title_el = card.select_one('h2, h3, h4, a, .title, [class*="title"]')
                    if title_el:
                        title = title_el.get_text(strip=True)
                        if title_el.name == 'a' and title_el.get('href'):
                            url = title_el['href']

                    loc_el = card.select_one('.location, [class*="location"], [class*="city"]')
                    if loc_el:
                        location = loc_el.get_text(strip=True)

                title = title.strip()
                if not title or len(title) < 3 or title.lower() in seen:
                    continue
                seen.add(title.lower())

                if url and url.startswith('/'):
                    url = base_url.rstrip('/') + url
                elif url and not url.startswith('http'):
                    url = base_url

                # Skip non-job items
                skip_words = ['about', 'contact', 'blog', 'home', 'sign in', 'privacy', 'terms', 'cookie']
                if any(sw in title.lower() for sw in skip_words):
                    continue

                raw = {
                    'id': '', 'title': title[:150], 'company': company_name,
                    'location': location, 'url': url, 'description': '',
                    'posted_date': '',
                }
                jobs.append(self._normalize_job(raw, source='darwinbox', ats='darwinbox', company_name=company_name))

        except ImportError:
            pass
        except Exception as e:
            print(f"  [Darwinbox] HTML parse error: {e}")

        if jobs:
            print(f"  [Darwinbox] Found {len(jobs)} jobs (HTML) for {company_name}")
        self._rate_limit()
        return jobs

    def scrape_search(self, query: str, location: str = None) -> List[Dict]:
        """Darwinbox doesn't support cross-company search"""
        return []
