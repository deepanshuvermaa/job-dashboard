"""
RemoteFront job board scraper.
Scrapes remote job listings from remotefront.com.
"""

import re
from typing import List, Dict
from .base_scraper import BaseBoardScraper


class RemoteFrontScraper(BaseBoardScraper):
    """Scraper for RemoteFront job board"""

    BASE_URL = "https://www.remotefront.com"

    def __init__(self, rate_limit_ms: int = 2000):
        super().__init__(rate_limit_ms)
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Referer': 'https://www.google.com/',
        })

    def scrape_company(self, company_url: str, company_name: str) -> List[Dict]:
        return self._scrape_page(company_url, company_name)

    def scrape_search(self, query: str, location: str = None) -> List[Dict]:
        """Search RemoteFront for jobs"""
        slug = query.lower().replace(' ', '-')
        print(f"  [RemoteFront] Searching for '{query}'")

        urls_to_try = [
            f"{self.BASE_URL}/remote-jobs/{slug}",
            f"{self.BASE_URL}/search?q={query.replace(' ', '+')}",
            f"{self.BASE_URL}/remote-developer-jobs",
        ]

        for url in urls_to_try:
            jobs = self._scrape_page(url, query)
            if jobs:
                return jobs

        return []

    def _scrape_page(self, url: str, context: str) -> List[Dict]:
        """Scrape a RemoteFront page"""
        response = self._safe_get(url)
        if not response or response.status_code != 200:
            return []

        jobs = []
        try:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(response.text, 'html.parser')

            all_links = soup.find_all('a', href=True)
            job_links = [l for l in all_links if any(kw in l.get('href', '') for kw in ['/job/', '/position/', '/remote-'])]

            seen = set()
            for link in job_links[:50]:
                title = link.get_text(strip=True)
                href = link.get('href', '')

                if not title or len(title) < 5 or title.lower() in seen:
                    continue
                seen.add(title.lower())

                if href and not href.startswith('http'):
                    href = f"{self.BASE_URL}{href}"

                raw = {
                    'id': '', 'title': title[:150], 'company': 'RemoteFront',
                    'location': 'Remote', 'url': href or url,
                    'description': '', 'posted_date': '',
                }
                jobs.append(self._normalize_job(raw, source='remotefront', ats='remotefront', company_name='RemoteFront'))

        except ImportError:
            pass
        except Exception as e:
            print(f"  [RemoteFront] Parse error: {e}")

        print(f"  [RemoteFront] Found {len(jobs)} jobs")
        self._rate_limit()
        return jobs
