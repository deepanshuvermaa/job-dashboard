"""
Base scraper class for all job board scrapers.
All scrapers normalize output to a standard job schema.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Optional
import time
import requests
from datetime import datetime


class BaseBoardScraper(ABC):
    """Base class for all job board scrapers"""

    def __init__(self, rate_limit_ms: int = 1000):
        self.rate_limit_ms = rate_limit_ms
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/html, */*',
            'Accept-Language': 'en-US,en;q=0.9',
        })

    @abstractmethod
    def scrape_company(self, company_url: str, company_name: str) -> List[Dict]:
        """Scrape all jobs from a company's career page"""
        pass

    def scrape_search(self, query: str, location: str = None) -> List[Dict]:
        """Scrape jobs from search query on board (override in subclasses that support search)"""
        return []

    def _normalize_job(self, raw: dict, source: str, ats: str, company_name: str = None) -> Dict:
        """Normalize job data to standard schema"""
        return {
            'id': str(raw.get('id', '')),
            'title': raw.get('title', '').strip(),
            'company': company_name or raw.get('company', '').strip(),
            'location': raw.get('location', 'Not specified').strip(),
            'job_url': raw.get('url', ''),
            'description_snippet': (raw.get('description', '') or '')[:500],
            'posted_date': raw.get('posted_date', ''),
            'source': source,
            'ats_type': ats,
            'scraped_at': datetime.now().isoformat(),
            'easy_apply': False,
            'salary': raw.get('salary'),
            'department': raw.get('department', ''),
            'employment_type': raw.get('employment_type', ''),
        }

    def _rate_limit(self):
        """Respect rate limits between requests"""
        time.sleep(self.rate_limit_ms / 1000)

    def _safe_get(self, url: str, **kwargs) -> Optional[requests.Response]:
        """Make a safe HTTP GET request with error handling"""
        try:
            response = self.session.get(url, timeout=30, **kwargs)
            response.raise_for_status()
            return response
        except requests.RequestException as e:
            print(f"  [ERROR] GET {url}: {e}")
            return None

    def _safe_post(self, url: str, **kwargs) -> Optional[requests.Response]:
        """Make a safe HTTP POST request with error handling"""
        try:
            response = self.session.post(url, timeout=30, **kwargs)
            response.raise_for_status()
            return response
        except requests.RequestException as e:
            print(f"  [ERROR] POST {url}: {e}")
            return None
