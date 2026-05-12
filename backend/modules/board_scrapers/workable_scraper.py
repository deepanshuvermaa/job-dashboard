"""
Workable ATS job board scraper.
Uses the Workable widget API.
"""

import re
from typing import List, Dict
from .base_scraper import BaseBoardScraper


class WorkableScraper(BaseBoardScraper):
    """Scraper for Workable ATS job boards"""

    def __init__(self, rate_limit_ms: int = 1500):
        super().__init__(rate_limit_ms)

    def _extract_slug(self, url: str) -> str:
        match = re.search(r'apply\.workable\.com/([^/?#]+)', url)
        if match:
            return match.group(1)
        match = re.search(r'jobs\.workable\.com/([^/?#]+)', url)
        if match:
            return match.group(1)
        return url.rstrip('/').split('/')[-1]

    def scrape_company(self, company_url: str, company_name: str) -> List[Dict]:
        slug = self._extract_slug(company_url)
        print(f"  [Workable] Fetching jobs for '{company_name}' (slug: {slug})")

        # Try multiple API formats
        apis = [
            (f"https://apply.workable.com/api/v3/accounts/{slug}/jobs", "POST", {"query": "", "location": "", "department": "", "worktype": "", "remote": []}),
            (f"https://apply.workable.com/api/v1/widget/accounts/{slug}", "GET", None),
            (f"https://apply.workable.com/{slug}/", "GET_HTML", None),
        ]

        for api_url, method, payload in apis:
            try:
                if method == "POST":
                    response = self._safe_post(api_url, json=payload, headers={
                        **self.session.headers,
                        'Content-Type': 'application/json',
                        'Accept': 'application/json',
                    })
                elif method == "GET":
                    response = self._safe_get(api_url)
                else:
                    response = self._safe_get(api_url)

                if not response or response.status_code != 200:
                    continue

                if method == "GET_HTML":
                    return self._parse_html(response.text, slug, company_name)

                data = response.json()

                # v3 format
                if isinstance(data, dict) and 'results' in data:
                    return self._parse_v3(data, slug, company_name)

                # v1 widget format
                if isinstance(data, dict) and 'jobs' in data:
                    return self._parse_v1(data, slug, company_name)

                # Direct array
                if isinstance(data, list):
                    return self._parse_list(data, slug, company_name)

            except Exception as e:
                continue

        print(f"  [Workable] No working API found for {company_name}")
        return []

    def _parse_v3(self, data: dict, slug: str, company_name: str) -> List[Dict]:
        jobs = []
        for item in data.get('results', []):
            raw = {
                'id': item.get('shortcode', ''),
                'title': item.get('title', ''),
                'company': company_name,
                'location': item.get('location', {}).get('location_str', '') if isinstance(item.get('location'), dict) else str(item.get('location', '')),
                'url': f"https://apply.workable.com/{slug}/j/{item.get('shortcode', '')}/",
                'description': item.get('description', '')[:500] if item.get('description') else '',
                'posted_date': item.get('published', ''),
                'department': item.get('department', ''),
                'employment_type': item.get('employment_type', ''),
            }
            jobs.append(self._normalize_job(raw, source='workable', ats='workable', company_name=company_name))

        next_token = data.get('nextPage')
        # Could fetch more pages here if needed

        print(f"  [Workable] Found {len(jobs)} jobs for {company_name}")
        self._rate_limit()
        return jobs

    def _parse_v1(self, data: dict, slug: str, company_name: str) -> List[Dict]:
        jobs = []
        for item in data.get('jobs', []):
            raw = {
                'id': item.get('shortcode', item.get('id', '')),
                'title': item.get('title', ''),
                'company': company_name,
                'location': item.get('city', '') or item.get('location', ''),
                'url': item.get('url', f"https://apply.workable.com/{slug}/"),
                'description': '',
                'posted_date': item.get('published', ''),
            }
            jobs.append(self._normalize_job(raw, source='workable', ats='workable', company_name=company_name))

        print(f"  [Workable] Found {len(jobs)} jobs for {company_name} (v1)")
        self._rate_limit()
        return jobs

    def _parse_list(self, data: list, slug: str, company_name: str) -> List[Dict]:
        jobs = []
        for item in data:
            if isinstance(item, dict) and item.get('title'):
                raw = {
                    'id': item.get('id', ''),
                    'title': item.get('title', ''),
                    'company': company_name,
                    'location': item.get('location', ''),
                    'url': item.get('url', f"https://apply.workable.com/{slug}/"),
                    'description': '',
                    'posted_date': '',
                }
                jobs.append(self._normalize_job(raw, source='workable', ats='workable', company_name=company_name))
        print(f"  [Workable] Found {len(jobs)} jobs for {company_name} (list)")
        self._rate_limit()
        return jobs

    def _parse_html(self, html: str, slug: str, company_name: str) -> List[Dict]:
        """Fallback: parse HTML career page"""
        jobs = []
        try:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html, 'html.parser')

            links = soup.find_all('a', href=True)
            seen = set()
            for link in links:
                href = link.get('href', '')
                text = link.get_text(strip=True)
                if f'/{slug}/j/' in href and text and text.lower() not in seen:
                    seen.add(text.lower())
                    if not href.startswith('http'):
                        href = f"https://apply.workable.com{href}"
                    raw = {
                        'id': '', 'title': text[:150], 'company': company_name,
                        'location': '', 'url': href, 'description': '', 'posted_date': '',
                    }
                    jobs.append(self._normalize_job(raw, source='workable', ats='workable', company_name=company_name))
        except:
            pass
        print(f"  [Workable] Found {len(jobs)} jobs (HTML) for {company_name}")
        self._rate_limit()
        return jobs

    def scrape_search(self, query: str, location: str = None) -> List[Dict]:
        """Workable doesn't support cross-company search"""
        return []
