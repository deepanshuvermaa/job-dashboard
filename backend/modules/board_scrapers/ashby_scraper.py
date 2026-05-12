"""
Ashby job board scraper.
Uses the public Ashby GraphQL API.
API: https://jobs.ashbyhq.com/api/non-user-graphql
"""

import re
from typing import List, Dict
from .base_scraper import BaseBoardScraper


class AshbyScraper(BaseBoardScraper):
    """Scraper for Ashby ATS job boards"""

    API_URL = "https://jobs.ashbyhq.com/api/non-user-graphql"

    def __init__(self, rate_limit_ms: int = 1500):
        super().__init__(rate_limit_ms)

    def _extract_org_slug(self, url: str) -> str:
        """Extract org slug from Ashby URL"""
        # Handles: https://jobs.ashbyhq.com/companyname
        match = re.search(r'jobs\.ashbyhq\.com/([^/?#]+)', url)
        if match:
            return match.group(1)
        return url.rstrip('/').split('/')[-1]

    def scrape_company(self, company_url: str, company_name: str) -> List[Dict]:
        """Scrape all jobs from an Ashby company board using GraphQL"""
        org_slug = self._extract_org_slug(company_url)

        print(f"  [Ashby] Fetching jobs for '{company_name}' (org: {org_slug})")

        # Ashby GraphQL query — jobs are on jobPostings, not under teams
        query = {
            "operationName": "ApiJobBoardWithTeams",
            "variables": {
                "organizationHostedJobsPageName": org_slug
            },
            "query": """
                query ApiJobBoardWithTeams($organizationHostedJobsPageName: String!) {
                    jobBoard: jobBoardWithTeams(
                        organizationHostedJobsPageName: $organizationHostedJobsPageName
                    ) {
                        teams {
                            id
                            name
                        }
                        jobPostings {
                            id
                            title
                            teamId
                            locationName
                            employmentType
                            compensationTierSummary
                            secondaryLocations {
                                locationId
                                locationName
                            }
                        }
                    }
                }
            """
        }

        response = self._safe_post(
            self.API_URL,
            json=query,
            headers={**self.session.headers, 'Content-Type': 'application/json'}
        )

        if not response:
            return []

        try:
            data = response.json()
            board = data.get('data', {}).get('jobBoard') or {}
            postings = board.get('jobPostings', [])
            teams_list = board.get('teams', [])
        except Exception as e:
            print(f"  [Ashby] JSON parse error for {company_name}: {e}")
            return []

        # Build team ID -> name map
        team_map = {t.get('id', ''): t.get('name', '') for t in teams_list}

        normalized = []
        for job in postings:
            location = job.get('locationName', 'Not specified')
            secondary = job.get('secondaryLocations', [])
            if secondary:
                extra_locs = [s.get('locationName', '') for s in secondary if s.get('locationName')]
                if extra_locs:
                    location = f"{location}, {', '.join(extra_locs)}"

            team_name = team_map.get(job.get('teamId', ''), '')

            raw = {
                'id': job.get('id', ''),
                'title': job.get('title', ''),
                'company': company_name,
                'location': location,
                'url': f"https://jobs.ashbyhq.com/{org_slug}/{job.get('id', '')}",
                'description': '',
                'posted_date': '',
                'department': team_name,
                'employment_type': job.get('employmentType', ''),
                'salary': job.get('compensationTierSummary', ''),
            }

            normalized.append(self._normalize_job(raw, source='ashby', ats='ashby', company_name=company_name))

        print(f"  [Ashby] Found {len(normalized)} jobs for {company_name}")
        self._rate_limit()
        return normalized
