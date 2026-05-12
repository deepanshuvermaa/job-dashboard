"""Monitor GitHub activity for content ideas"""
import httpx
from datetime import datetime, timedelta
from typing import List, Dict

class GitHubMonitor:
    """Monitor GitHub repos for content-worthy activities"""

    def __init__(self, github_token: str, username: str):
        self.token = github_token
        self.username = username
        self.headers = {
            "Authorization": f"token {github_token}",
            "Accept": "application/vnd.github.v3+json"
        }

    async def get_recent_activities(self, days=7) -> List[Dict]:
        """Get recent GitHub activities"""
        activities = []

        # Get recent commits
        commits = await self._get_recent_commits(days)
        activities.extend(commits)

        # Get recent PRs
        prs = await self._get_recent_prs(days)
        activities.extend(prs)

        # Get recent releases
        releases = await self._get_recent_releases(days)
        activities.extend(releases)

        return activities

    async def _get_recent_commits(self, days) -> List[Dict]:
        """Get recent commits across all repos"""
        since = (datetime.now() - timedelta(days=days)).isoformat()

        async with httpx.AsyncClient() as client:
            # Get user's repos
            response = await client.get(
                f"https://api.github.com/users/{self.username}/repos",
                headers=self.headers
            )
            repos = response.json()

            commits = []
            for repo in repos[:10]:  # Limit to 10 repos
                try:
                    commit_response = await client.get(
                        f"https://api.github.com/repos/{self.username}/{repo['name']}/commits",
                        headers=self.headers,
                        params={"since": since, "author": self.username}
                    )

                    repo_commits = commit_response.json()
                    for commit in repo_commits:
                        commits.append({
                            "type": "commit",
                            "repo": repo['name'],
                            "message": commit['commit']['message'],
                            "date": commit['commit']['author']['date'],
                            "url": commit['html_url'],
                            "content_potential": self._score_commit(commit['commit']['message'])
                        })
                except:
                    continue

            return commits

    async def _get_recent_prs(self, days) -> List[Dict]:
        """Get recent pull requests"""
        since = (datetime.now() - timedelta(days=days)).isoformat()

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"https://api.github.com/search/issues",
                headers=self.headers,
                params={
                    "q": f"author:{self.username} type:pr created:>{since[:10]}",
                    "sort": "created",
                    "order": "desc"
                }
            )

            prs = []
            for pr in response.json().get('items', []):
                prs.append({
                    "type": "pull_request",
                    "title": pr['title'],
                    "repo": pr['repository_url'].split('/')[-1],
                    "body": pr.get('body', ''),
                    "date": pr['created_at'],
                    "url": pr['html_url'],
                    "content_potential": "high"  # PRs are usually good content
                })

            return prs

    async def _get_recent_releases(self, days) -> List[Dict]:
        """Get recent releases"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"https://api.github.com/users/{self.username}/repos",
                headers=self.headers
            )
            repos = response.json()

            releases = []
            for repo in repos[:10]:
                try:
                    release_response = await client.get(
                        f"https://api.github.com/repos/{self.username}/{repo['name']}/releases",
                        headers=self.headers
                    )

                    for release in release_response.json()[:3]:
                        release_date = datetime.fromisoformat(release['created_at'].replace('Z', '+00:00'))
                        if (datetime.now(release_date.tzinfo) - release_date).days <= days:
                            releases.append({
                                "type": "release",
                                "repo": repo['name'],
                                "version": release['tag_name'],
                                "title": release['name'],
                                "body": release.get('body', ''),
                                "date": release['created_at'],
                                "url": release['html_url'],
                                "content_potential": "high"
                            })
                except:
                    continue

            return releases

    def _score_commit(self, message: str) -> str:
        """Score content potential of commit"""
        message_lower = message.lower()

        high_value_keywords = [
            "refactor", "optimize", "improve", "fix", "bug", "security",
            "performance", "architecture", "implement", "add feature"
        ]

        low_value_keywords = [
            "typo", "formatting", "update readme", "merge", "bump version"
        ]

        if any(kw in message_lower for kw in high_value_keywords):
            return "high"
        elif any(kw in message_lower for kw in low_value_keywords):
            return "low"
        else:
            return "medium"

    def extract_tech_stack(self, activities: List[Dict]) -> List[str]:
        """Extract technologies from activities"""
        tech_keywords = set()

        for activity in activities:
            text = activity.get('message', '') + ' ' + activity.get('body', '') + ' ' + activity.get('title', '')
            text = text.lower()

            # Common tech stack keywords
            technologies = [
                'python', 'javascript', 'typescript', 'react', 'vue', 'angular',
                'node', 'express', 'fastapi', 'django', 'flask',
                'postgresql', 'mongodb', 'redis', 'docker', 'kubernetes',
                'aws', 'azure', 'gcp', 'terraform', 'ci/cd'
            ]

            for tech in technologies:
                if tech in text:
                    tech_keywords.add(tech)

        return list(tech_keywords)
