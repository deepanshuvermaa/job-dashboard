"""
Reddit job board scraper.
Uses the public Reddit JSON API (no auth needed).
Scrapes job posts from hiring/remote work subreddits.
"""

import re
import time
from typing import List, Dict
from datetime import datetime
from .base_scraper import BaseBoardScraper


# Subreddits known for job postings
DEFAULT_SUBREDDITS = [
    'remotework', 'WorkOnline', 'freelance', 'forhire', 'hiring',
    'jobbit', 'remotejobs', 'digitalnomad', 'webdev',
    'datascience', 'learnprogramming',
]

# Patterns that indicate a post is a job listing (not a question/discussion)
HIRING_PATTERNS = [
    r'\[hiring\]', r'\[for hire\]', r'\bhiring\b', r'\bwe.re hiring\b',
    r'\bjob opening\b', r'\bopen position\b', r'\blooking for\b',
    r'\bremote\b.*\b(developer|engineer|designer)\b',
    r'\$\d+[kK]?', r'\b(salary|compensation|pay)\b.*\$',
    r'\b(full.?time|part.?time|contract|freelance)\b',
    r'\bapply\b', r'\bresume\b', r'\bCV\b',
]


class RedditScraper(BaseBoardScraper):
    """Scraper for Reddit job subreddits"""

    def __init__(self, rate_limit_ms: int = 2000):
        super().__init__(rate_limit_ms)
        self.session.headers.update({
            'User-Agent': 'JobScraperBot/1.0 (LinkedIn Automation Suite)',
        })

    def scrape_company(self, company_url: str, company_name: str) -> List[Dict]:
        """Scrape a specific subreddit URL"""
        # Extract subreddit name from URL
        match = re.search(r'r/([^/?#]+)', company_url)
        if match:
            return self.scrape_subreddit(match.group(1), company_name)
        return []

    def scrape_search(self, query: str, location: str = None) -> List[Dict]:
        """Search across all default hiring subreddits for a query"""
        all_jobs = []
        for sub in DEFAULT_SUBREDDITS:
            try:
                jobs = self.scrape_subreddit(sub, sub, keyword_filter=query)
                all_jobs.extend(jobs)
            except Exception as e:
                print(f"  [Reddit] Error scraping r/{sub}: {e}")
            self._rate_limit()

        print(f"  [Reddit] Total from search '{query}': {len(all_jobs)} jobs")
        return all_jobs

    def scrape_subreddit(self, subreddit: str, display_name: str = None,
                         keyword_filter: str = None, limit: int = 50) -> List[Dict]:
        """Scrape job posts from a subreddit"""
        display_name = display_name or subreddit
        print(f"  [Reddit] Scraping r/{subreddit}...")

        all_posts = []
        after = None

        # Fetch up to 2 pages (50 posts each)
        for page in range(2):
            url = f"https://www.reddit.com/r/{subreddit}/new.json?limit=50&raw_json=1"
            if after:
                url += f"&after={after}"

            response = self._safe_get(url)
            if not response:
                break

            try:
                data = response.json()
                posts = data.get('data', {}).get('children', [])
                after = data.get('data', {}).get('after')
            except Exception as e:
                print(f"  [Reddit] JSON parse error for r/{subreddit}: {e}")
                break

            for post in posts:
                post_data = post.get('data', {})

                # Skip stickied/pinned posts (usually rules)
                if post_data.get('stickied'):
                    continue

                title = post_data.get('title', '')
                selftext = post_data.get('selftext', '')
                full_text = f"{title} {selftext}".lower()

                # Check if this looks like a job posting
                is_job = any(re.search(pattern, full_text, re.IGNORECASE) for pattern in HIRING_PATTERNS)
                if not is_job:
                    continue

                # Apply keyword filter if provided
                if keyword_filter:
                    kw_lower = keyword_filter.lower()
                    if kw_lower not in full_text:
                        continue

                # Extract salary if mentioned
                salary = None
                salary_match = re.search(r'\$[\d,]+[kK]?\s*[-–]\s*\$[\d,]+[kK]?', full_text)
                if salary_match:
                    salary = salary_match.group(0)
                else:
                    salary_match = re.search(r'\$[\d,]+[kK]?\+?(?:\s*/\s*(?:hr|hour|year|yr|mo|month))?', full_text)
                    if salary_match:
                        salary = salary_match.group(0)

                # Extract location hints
                location = 'Remote'
                loc_match = re.search(r'\b(remote|on.?site|hybrid)\b', full_text, re.IGNORECASE)
                if loc_match:
                    location = loc_match.group(0).title()
                loc_match2 = re.search(r'\b(USA|US|UK|EU|India|Canada|worldwide|global)\b', full_text, re.IGNORECASE)
                if loc_match2:
                    location += f" ({loc_match2.group(0).upper()})"

                # Extract company name from post if possible
                company = f"r/{subreddit}"
                company_match = re.search(r'(?:at|@|for|with)\s+([A-Z][A-Za-z0-9\s&.]+?)(?:\s*[-|,.\[]|$)', title)
                if company_match:
                    company = company_match.group(1).strip()

                # Build job title from post title
                job_title = title[:120]
                # Clean up common prefixes
                for prefix in ['[Hiring]', '[For Hire]', '[HIRING]', '[FOR HIRE]']:
                    job_title = job_title.replace(prefix, '').strip()

                created_utc = post_data.get('created_utc', 0)
                posted_date = datetime.fromtimestamp(created_utc).isoformat() if created_utc else ''

                raw = {
                    'id': post_data.get('id', ''),
                    'title': job_title,
                    'company': company,
                    'location': location,
                    'url': f"https://www.reddit.com{post_data.get('permalink', '')}",
                    'description': selftext[:500] if selftext else title,
                    'posted_date': posted_date,
                    'salary': salary,
                    'department': f"r/{subreddit}",
                }

                all_posts.append(self._normalize_job(
                    raw, source='reddit', ats='reddit', company_name=company
                ))

            if not after:
                break
            self._rate_limit()

        print(f"  [Reddit] Found {len(all_posts)} job posts in r/{subreddit}")
        return all_posts

    def scrape_all_subreddits(self, subreddits: List[str] = None,
                               keyword_filter: str = None) -> List[Dict]:
        """Scrape all configured subreddits"""
        subs = subreddits or DEFAULT_SUBREDDITS
        all_jobs = []

        print(f"\n  [Reddit] Scanning {len(subs)} subreddits...")
        for sub in subs:
            try:
                jobs = self.scrape_subreddit(sub, keyword_filter=keyword_filter)
                all_jobs.extend(jobs)
            except Exception as e:
                print(f"  [Reddit] Error r/{sub}: {e}")
            self._rate_limit()

        print(f"  [Reddit] Total: {len(all_jobs)} job posts from {len(subs)} subreddits")
        return all_jobs
