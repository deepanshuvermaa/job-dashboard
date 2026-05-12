"""
DailyRemote job board scraper.
Scrapes remote job listings from dailyremote.com.
"""

import re
from typing import List, Dict
from .base_scraper import BaseBoardScraper


class DailyRemoteScraper(BaseBoardScraper):
    """Scraper for DailyRemote job board"""

    BASE_URL = "https://dailyremote.com"

    def __init__(self, rate_limit_ms: int = 2000):
        super().__init__(rate_limit_ms)

    def scrape_company(self, company_url: str, company_name: str) -> List[Dict]:
        return self._scrape_page(company_url, company_name)

    def scrape_search(self, query: str, location: str = None) -> List[Dict]:
        """Search DailyRemote for jobs"""
        slug = query.lower().replace(' ', '-')
        print(f"  [DailyRemote] Searching for '{query}'")

        # Try multiple URL patterns (site structure changes frequently)
        urls_to_try = [
            f"{self.BASE_URL}/remote-{slug}-jobs",
            f"{self.BASE_URL}/remote-jobs/{slug}",
            f"{self.BASE_URL}/remote-developer-jobs",
        ]

        for url in urls_to_try:
            jobs = self._scrape_page(url, query)
            if jobs:
                return jobs

        print(f"  [DailyRemote] No results found for '{query}'")
        return []

    def _scrape_page(self, url: str, context: str) -> List[Dict]:
        """Scrape a DailyRemote page for job listings"""
        response = self._safe_get(url)
        if not response or response.status_code != 200:
            return []

        jobs = []
        try:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(response.text, 'html.parser')

            # Find job cards - try multiple selectors
            selectors = [
                'a.job-card', '.job-listing a', 'a[href*="/remote-job/"]',
                '.card a[href*="job"]', 'article a', '.job-item',
            ]

            cards = []
            for sel in selectors:
                cards = soup.select(sel)
                if cards:
                    break

            # Fallback: find all links that look like job listings
            if not cards:
                all_links = soup.find_all('a', href=True)
                cards = [l for l in all_links if '/remote-job/' in l.get('href', '') or '/job/' in l.get('href', '')]

            seen = set()
            for card in cards[:50]:
                title = card.get_text(strip=True)
                href = card.get('href', '')

                if not title or len(title) < 5 or title.lower() in seen:
                    continue
                seen.add(title.lower())

                if href and not href.startswith('http'):
                    href = f"{self.BASE_URL}{href}"

                raw = {
                    'id': '', 'title': title[:150], 'company': 'DailyRemote',
                    'location': 'Remote', 'url': href or url,
                    'description': '', 'posted_date': '',
                }
                jobs.append(self._normalize_job(raw, source='dailyremote', ats='dailyremote', company_name='DailyRemote'))

        except ImportError:
            print("  [DailyRemote] BeautifulSoup not installed")
        except Exception as e:
            print(f"  [DailyRemote] Parse error: {e}")

        print(f"  [DailyRemote] Found {len(jobs)} jobs from {url}")
        self._rate_limit()
        return jobs
