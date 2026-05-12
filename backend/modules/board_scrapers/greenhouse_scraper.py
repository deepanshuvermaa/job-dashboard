"""
Greenhouse job board scraper.
Uses the public Greenhouse Boards API (no auth needed).
API: https://boards-api.greenhouse.io/v1/boards/{board_token}/jobs
"""

import re
from typing import List, Dict
from .base_scraper import BaseBoardScraper


class GreenhouseScraper(BaseBoardScraper):
    """Scraper for Greenhouse ATS job boards"""

    API_BASE = "https://boards-api.greenhouse.io/v1/boards"

    def __init__(self, rate_limit_ms: int = 1000):
        super().__init__(rate_limit_ms)

    def _extract_board_token(self, url: str) -> str:
        """Extract board token from Greenhouse URL"""
        # Handles: https://boards.greenhouse.io/companyname
        # Also: https://boards.greenhouse.io/companyname/jobs/123
        # Also: https://job-boards.greenhouse.io/companyname
        patterns = [
            r'boards\.greenhouse\.io/([^/?#]+)',
            r'job-boards\.greenhouse\.io/([^/?#]+)',
        ]
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        # Fallback: use the last path segment
        return url.rstrip('/').split('/')[-1]

    def scrape_company(self, company_url: str, company_name: str, posted_after: str = None) -> List[Dict]:
        """Scrape all jobs from a Greenhouse company board"""
        board_token = self._extract_board_token(company_url)
        api_url = f"{self.API_BASE}/{board_token}/jobs?content=true"

        print(f"  [Greenhouse] Fetching jobs for '{company_name}' (board: {board_token})")

        response = self._safe_get(api_url)
        if not response:
            return []

        try:
            data = response.json()
            jobs = data.get('jobs', [])
        except Exception as e:
            print(f"  [Greenhouse] JSON parse error for {company_name}: {e}")
            return []

        normalized = []
        for job in jobs:
            location_name = "Not specified"
            if job.get('location', {}).get('name'):
                location_name = job['location']['name']

            # Strip HTML from description
            desc = job.get('content', '') or ''
            desc = re.sub(r'<[^>]+>', ' ', desc)
            desc = re.sub(r'\s+', ' ', desc).strip()

            raw = {
                'id': str(job.get('id', '')),
                'title': job.get('title', ''),
                'company': company_name,
                'location': location_name,
                'url': f"https://boards.greenhouse.io/{board_token}/jobs/{job.get('id', '')}",
                'description': desc,
                'posted_date': job.get('updated_at', ''),
                'department': '',
            }

            # Extract department if present
            if job.get('departments'):
                raw['department'] = job['departments'][0].get('name', '')

            normalized.append(self._normalize_job(raw, source='greenhouse', ats='greenhouse', company_name=company_name))

        # Apply date filter if posted_after is set
        if posted_after:
            from datetime import datetime
            try:
                cutoff = datetime.fromisoformat(posted_after.replace('Z', '+00:00')) if isinstance(posted_after, str) else posted_after
                before_filter = len(normalized)
                normalized = [j for j in normalized if j.get('posted_date') and j['posted_date'] >= posted_after]
                print(f"  [Greenhouse] Date filter: {before_filter} -> {len(normalized)} jobs (after {posted_after})")
            except:
                pass

        print(f"  [Greenhouse] Found {len(normalized)} jobs for {company_name}")
        self._rate_limit()
        return normalized

    def scrape_search(self, query: str, location: str = None) -> List[Dict]:
        """Greenhouse doesn't support cross-board search - use scrape_company instead"""
        return []
