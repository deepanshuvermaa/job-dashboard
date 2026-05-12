"""
Structured Data (JSON-LD / schema.org) job scraper.
Many modern career pages embed schema.org/JobPosting structured data.
This scraper extracts jobs from those JSON-LD blocks.
Companies like Google, Amazon, Microsoft use this format.
"""

import re
import json
from typing import List, Dict
from .base_scraper import BaseBoardScraper


class StructuredDataScraper(BaseBoardScraper):
    """Scraper that extracts jobs from schema.org/JobPosting JSON-LD blocks"""

    def __init__(self, rate_limit_ms: int = 2000):
        super().__init__(rate_limit_ms)

    def scrape_company(self, company_url: str, company_name: str) -> List[Dict]:
        """Scrape jobs from a page with schema.org/JobPosting structured data"""
        print(f"  [StructuredData] Fetching '{company_name}': {company_url}")

        response = self._safe_get(company_url)
        if not response:
            return []

        html = response.text
        jobs = []

        # Extract all JSON-LD blocks
        json_ld_blocks = re.findall(
            r'<script[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
            html, re.DOTALL | re.IGNORECASE
        )

        for block in json_ld_blocks:
            try:
                data = json.loads(block.strip())
                # Handle both single objects and arrays
                if isinstance(data, list):
                    for item in data:
                        job = self._extract_job_posting(item, company_name, company_url)
                        if job:
                            jobs.append(job)
                elif isinstance(data, dict):
                    if data.get('@type') == 'JobPosting':
                        job = self._extract_job_posting(data, company_name, company_url)
                        if job:
                            jobs.append(job)
                    # Check for @graph containing job postings
                    elif '@graph' in data:
                        for item in data['@graph']:
                            job = self._extract_job_posting(item, company_name, company_url)
                            if job:
                                jobs.append(job)
                    # Check for itemListElement
                    elif 'itemListElement' in data:
                        for item in data['itemListElement']:
                            inner = item.get('item', item)
                            job = self._extract_job_posting(inner, company_name, company_url)
                            if job:
                                jobs.append(job)
            except json.JSONDecodeError:
                continue

        print(f"  [StructuredData] Found {len(jobs)} jobs for {company_name}")
        self._rate_limit()
        return jobs

    def _extract_job_posting(self, data: dict, company_name: str, base_url: str) -> Dict:
        """Extract a normalized job from a schema.org/JobPosting object"""
        if not isinstance(data, dict):
            return None
        if data.get('@type') != 'JobPosting':
            return None

        title = data.get('title', '')
        if not title:
            return None

        # Extract location
        location = 'Not specified'
        job_location = data.get('jobLocation')
        if isinstance(job_location, dict):
            address = job_location.get('address', {})
            if isinstance(address, dict):
                parts = [address.get('addressLocality', ''), address.get('addressRegion', ''), address.get('addressCountry', '')]
                location = ', '.join(p for p in parts if p)
            elif isinstance(address, str):
                location = address
        elif isinstance(job_location, list) and job_location:
            first = job_location[0]
            if isinstance(first, dict):
                address = first.get('address', {})
                if isinstance(address, dict):
                    parts = [address.get('addressLocality', ''), address.get('addressRegion', '')]
                    location = ', '.join(p for p in parts if p)

        # Extract company name from data if available
        org = data.get('hiringOrganization', {})
        if isinstance(org, dict):
            org_name = org.get('name', '')
            if org_name:
                company_name = org_name

        # Extract salary
        salary = None
        base_salary = data.get('baseSalary', {})
        if isinstance(base_salary, dict):
            value = base_salary.get('value', {})
            currency = base_salary.get('currency', '')
            if isinstance(value, dict):
                min_val = value.get('minValue', '')
                max_val = value.get('maxValue', '')
                if min_val and max_val:
                    salary = f"{currency} {min_val}-{max_val}"
            elif value:
                salary = f"{currency} {value}"

        # Build URL
        url = data.get('url', base_url)
        if url and url.startswith('/'):
            from urllib.parse import urljoin
            url = urljoin(base_url, url)

        # Description
        desc = data.get('description', '')
        if desc:
            desc = re.sub(r'<[^>]+>', ' ', desc)
            desc = re.sub(r'\s+', ' ', desc).strip()[:500]

        raw = {
            'id': data.get('identifier', {}).get('value', '') if isinstance(data.get('identifier'), dict) else str(data.get('identifier', '')),
            'title': title,
            'company': company_name,
            'location': location or 'Not specified',
            'url': url,
            'description': desc,
            'posted_date': data.get('datePosted', ''),
            'salary': salary,
            'employment_type': data.get('employmentType', ''),
        }

        return self._normalize_job(raw, source='structured_data', ats='structured_data', company_name=company_name)
