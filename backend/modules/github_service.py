"""
GitHub API Service - Fetch real commits and PRs
"""

import os
import requests
from datetime import datetime, timedelta
from typing import List, Dict

class GitHubService:
    def __init__(self, token: str = None):
        self.token = token or os.getenv('GITHUB_TOKEN')
        self.base_url = 'https://api.github.com'
        self.headers = {
            'Authorization': f'token {self.token}',
            'Accept': 'application/vnd.github.v3+json'
        }

    def get_repo_commits(self, repo_name: str, days: int = 7, limit: int = 30) -> List[Dict]:
        """Get recent commits from a repository"""
        try:
            since_date = (datetime.now() - timedelta(days=days)).isoformat()
            url = f'{self.base_url}/repos/{repo_name}/commits'
            params = {'since': since_date, 'per_page': limit}

            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()

            commits = []
            for commit in response.json():
                commit_date = datetime.strptime(commit['commit']['author']['date'], '%Y-%m-%dT%H:%M:%SZ')
                days_ago = (datetime.now() - commit_date).days

                commits.append({
                    'sha': commit['sha'][:7],
                    'message': commit['commit']['message'],
                    'author': commit['commit']['author']['name'],
                    'date': commit['commit']['author']['date'],
                    'days_ago': days_ago,
                    'url': commit['html_url']
                })

            return commits
        except Exception as e:
            print(f"Error fetching commits: {e}")
            return []

    def get_last_n_commits(self, repo_name: str, n: int = 5) -> List[Dict]:
        """Get last N commits from a repository"""
        try:
            url = f'{self.base_url}/repos/{repo_name}/commits'
            params = {'per_page': n}

            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()

            commits = []
            for commit in response.json():
                commit_date = datetime.strptime(commit['commit']['author']['date'], '%Y-%m-%dT%H:%M:%SZ')
                days_ago = (datetime.now() - commit_date).days

                # Format commit message (take first line only)
                message = commit['commit']['message'].split('\n')[0]

                commits.append({
                    'sha': commit['sha'][:7],
                    'message': message,
                    'author': commit['commit']['author']['name'],
                    'date': commit['commit']['author']['date'],
                    'days_ago': days_ago,
                    'url': commit['html_url']
                })

            return commits
        except Exception as e:
            print(f"Error fetching commits: {e}")
            return []

    def get_repo_prs(self, repo_name: str, days: int = 7) -> List[Dict]:
        """Get recent pull requests from a repository"""
        try:
            url = f'{self.base_url}/repos/{repo_name}/pulls'
            params = {'state': 'all', 'per_page': 30, 'sort': 'updated', 'direction': 'desc'}

            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()

            cutoff_date = datetime.now() - timedelta(days=days)
            prs = []

            for pr in response.json():
                pr_date = datetime.strptime(pr['updated_at'], '%Y-%m-%dT%H:%M:%SZ')
                if pr_date >= cutoff_date:
                    prs.append({
                        'number': pr['number'],
                        'title': pr['title'],
                        'state': pr['state'],
                        'author': pr['user']['login'],
                        'created_at': pr['created_at'],
                        'merged': pr.get('merged_at') is not None,
                        'url': pr['html_url']
                    })

            return prs
        except Exception as e:
            print(f"Error fetching PRs: {e}")
            return []

    def get_repo_activity_summary(self, repo_name: str, days: int = 7) -> Dict:
        """Get a summary of repository activity"""
        commits = self.get_repo_commits(repo_name, days)
        prs = self.get_repo_prs(repo_name, days)

        return {
            'repo_name': repo_name,
            'commits': commits,
            'commit_count': len(commits),
            'pull_requests': prs,
            'pr_count': len(prs),
            'time_period_days': days
        }

    def extract_topics_from_activity(self, activity: Dict) -> List[str]:
        """Extract topics/keywords from repository activity"""
        topics = set()

        # Extract from commit messages
        for commit in activity.get('commits', []):
            message = commit['message'].lower()
            # Simple keyword extraction
            keywords = ['fix', 'bug', 'feature', 'add', 'update', 'refactor',
                       'improve', 'implement', 'remove', 'delete', 'optimize']
            for keyword in keywords:
                if keyword in message:
                    topics.add(keyword)

        # Extract from PR titles
        for pr in activity.get('pull_requests', []):
            title = pr['title'].lower()
            for keyword in ['feature', 'bugfix', 'hotfix', 'enhancement', 'docs']:
                if keyword in title:
                    topics.add(keyword)

        return list(topics)

    def get_user_repos(self, username: str, sort: str = 'updated', per_page: int = 100) -> List[Dict]:
        """Get all repositories for a user"""
        try:
            url = f'{self.base_url}/users/{username}/repos'
            params = {
                'sort': sort,
                'per_page': per_page,
                'type': 'owner'  # Only repos owned by user
            }

            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()

            repos = []
            for repo in response.json():
                # Calculate days since last update
                updated_at = datetime.strptime(repo['updated_at'], '%Y-%m-%dT%H:%M:%SZ')
                days_ago = (datetime.now() - updated_at).days

                repos.append({
                    'name': repo['name'],
                    'full_name': repo['full_name'],
                    'description': repo['description'] or 'No description',
                    'html_url': repo['html_url'],
                    'language': repo['language'] or 'Unknown',
                    'stars': repo['stargazers_count'],
                    'forks': repo['forks_count'],
                    'updated_at': repo['updated_at'],
                    'days_since_update': days_ago,
                    'is_private': repo['private'],
                    'is_fork': repo['fork']
                })

            return repos

        except Exception as e:
            print(f"Error fetching user repos: {e}")
            return []
