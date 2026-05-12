"""
Generic HTML Career Page Scraper.
Attempts to extract job listings from any HTML career page using common patterns.
Used as a fallback when no specific ATS is detected.
"""

import re
from typing import List, Dict
from .base_scraper import BaseBoardScraper


class GenericHTMLScraper(BaseBoardScraper):
    """Generic scraper that works on arbitrary career pages using heuristics"""

    def __init__(self, rate_limit_ms: int = 2000):
        super().__init__(rate_limit_ms)

    def scrape_company(self, company_url: str, company_name: str) -> List[Dict]:
        """Scrape job listings from a generic HTML career page"""
        print(f"  [GenericHTML] Scraping '{company_name}': {company_url}")

        response = self._safe_get(company_url)
        if not response:
            return []

        html = response.text
        jobs = []

        try:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html, 'html.parser')

            # Strategy 1: Look for common job listing container patterns
            job_selectors = [
                '.job-listing', '.job-card', '.job-item', '.career-item',
                '.position-card', '.opening-card', '.vacancy',
                '[class*="job-list"] li', '[class*="career"] li',
                '[class*="opening"] li', '[class*="position"] li',
                '.jobs-list li', '.careers-list li',
                'article[class*="job"]', 'div[class*="vacancy"]',
                'tr[class*="job"]', 'tr[class*="position"]',
            ]

            job_elements = []
            for selector in job_selectors:
                found = soup.select(selector)
                if len(found) >= 2:  # Need at least 2 to be a list
                    job_elements = found
                    break

            # Strategy 2: Look for links with job-like text
            if not job_elements:
                all_links = soup.find_all('a', href=True)
                job_links = []
                for link in all_links:
                    text = link.get_text(strip=True)
                    href = link['href']
                    # Filter for job-like links (contains /jobs/, /careers/, /apply, etc.)
                    if any(kw in href.lower() for kw in ['/job', '/career', '/position', '/opening', '/apply', '/vacancy']):
                        if len(text) > 5 and len(text) < 200:
                            job_links.append(link)

                if len(job_links) >= 2:
                    job_elements = job_links

            # Extract jobs from found elements
            seen_titles = set()
            for elem in job_elements[:100]:  # Cap at 100
                title = ''
                location = 'Not specified'
                url = company_url

                if elem.name == 'a':
                    title = elem.get_text(strip=True)
                    url = elem.get('href', '')
                else:
                    # Find title
                    title_el = elem.select_one('h2, h3, h4, a, .title, [class*="title"], [class*="name"]')
                    if title_el:
                        title = title_el.get_text(strip=True)
                        if title_el.name == 'a' and title_el.get('href'):
                            url = title_el['href']

                    # Find location
                    loc_el = elem.select_one('.location, [class*="location"], [class*="city"], [class*="place"]')
                    if loc_el:
                        location = loc_el.get_text(strip=True)

                    # Find link
                    if url == company_url:
                        link_el = elem.select_one('a[href]')
                        if link_el:
                            url = link_el['href']

                # Clean up
                title = title.strip()
                if not title or len(title) < 3 or title.lower() in seen_titles:
                    continue
                seen_titles.add(title.lower())

                # Make absolute URL
                if url.startswith('/'):
                    from urllib.parse import urljoin
                    url = urljoin(company_url, url)
                elif not url.startswith('http'):
                    url = company_url

                # Skip non-job items
                skip_words = ['about us', 'contact', 'blog', 'news', 'home', 'sign in', 'log in', 'privacy', 'terms']
                if any(sw in title.lower() for sw in skip_words):
                    continue

                raw = {
                    'id': '',
                    'title': title[:150],
                    'company': company_name,
                    'location': location,
                    'url': url,
                    'description': '',
                    'posted_date': '',
                }
                jobs.append(self._normalize_job(raw, source='career_page', ats='generic', company_name=company_name))

        except ImportError:
            print("  [GenericHTML] BeautifulSoup not installed")
        except Exception as e:
            print(f"  [GenericHTML] Error scraping {company_name}: {e}")

        print(f"  [GenericHTML] Found {len(jobs)} jobs for {company_name}")
        self._rate_limit()
        return jobs
