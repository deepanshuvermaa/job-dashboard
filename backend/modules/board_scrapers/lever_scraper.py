"""
Lever job board scraper.
Uses the public Lever API.
API: https://api.lever.co/v0/postings/{company}
"""

import re
from typing import List, Dict
from .base_scraper import BaseBoardScraper


class LeverScraper(BaseBoardScraper):
    """Scraper for Lever ATS job boards"""

    API_BASE = "https://api.lever.co/v0/postings"

    def __init__(self, rate_limit_ms: int = 1000):
        super().__init__(rate_limit_ms)

    def _extract_company_slug(self, url: str) -> str:
        """Extract company slug from Lever URL"""
        # Handles: https://jobs.lever.co/companyname
        # Also: https://lever.co/companyname
        patterns = [
            r'jobs\.lever\.co/([^/?#]+)',
            r'lever\.co/([^/?#]+)',
        ]
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return url.rstrip('/').split('/')[-1]

    def scrape_company(self, company_url: str, company_name: str, posted_after: str = None) -> List[Dict]:
        """Scrape all jobs from a Lever company board"""
        company_slug = self._extract_company_slug(company_url)
        api_url = f"{self.API_BASE}/{company_slug}"

        print(f"  [Lever] Fetching jobs for '{company_name}' (slug: {company_slug})")

        response = self._safe_get(api_url)
        if not response:
            return []

        try:
            jobs = response.json()
            if not isinstance(jobs, list):
                print(f"  [Lever] Unexpected response format for {company_name}")
                return []
        except Exception as e:
            print(f"  [Lever] JSON parse error for {company_name}: {e}")
            return []

        normalized = []
        for job in jobs:
            location = job.get('categories', {}).get('location', 'Not specified')
            department = job.get('categories', {}).get('department', '')
            team = job.get('categories', {}).get('team', '')
            commitment = job.get('categories', {}).get('commitment', '')

            # Strip HTML from description
            desc = job.get('descriptionPlain', '') or ''
            if not desc:
                desc_html = job.get('description', '') or ''
                desc = re.sub(r'<[^>]+>', ' ', desc_html)
                desc = re.sub(r'\s+', ' ', desc).strip()

            raw = {
                'id': job.get('id', ''),
                'title': job.get('text', ''),
                'company': company_name,
                'location': location,
                'url': job.get('hostedUrl', '') or job.get('applyUrl', ''),
                'description': desc,
                'posted_date': '',
                'department': department or team,
                'employment_type': commitment,
            }

            # Convert createdAt timestamp
            created_at = job.get('createdAt')
            if created_at:
                try:
                    from datetime import datetime
                    raw['posted_date'] = datetime.fromtimestamp(created_at / 1000).isoformat()
                except:
                    pass

            normalized.append(self._normalize_job(raw, source='lever', ats='lever', company_name=company_name))

        # Apply date filter if posted_after is set
        if posted_after:
            from datetime import datetime
            try:
                cutoff = datetime.fromisoformat(posted_after.replace('Z', '+00:00')) if isinstance(posted_after, str) else posted_after
                before_filter = len(normalized)
                normalized = [j for j in normalized if j.get('posted_date') and j['posted_date'] >= posted_after]
                print(f"  [Lever] Date filter: {before_filter} -> {len(normalized)} jobs (after {posted_after})")
            except:
                pass

        print(f"  [Lever] Found {len(normalized)} jobs for {company_name}")
        self._rate_limit()
        return normalized
