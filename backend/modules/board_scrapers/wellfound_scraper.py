"""
Wellfound (formerly AngelList) job board scraper.
Uses HTTP first, falls back to Selenium for Cloudflare-protected pages.
"""

import re
import time
from typing import List, Dict, Optional
from .base_scraper import BaseBoardScraper


class WellfoundScraper(BaseBoardScraper):
    """Scraper for Wellfound (AngelList Talent) job listings"""

    def __init__(self, rate_limit_ms: int = 2000):
        super().__init__(rate_limit_ms)
        self._driver = None

    def _get_driver(self):
        """Lazy-init Selenium driver only when HTTP fails"""
        if self._driver is None:
            try:
                from undetected_chromedriver import Chrome, ChromeOptions
                options = ChromeOptions()
                options.add_argument('--headless')
                options.add_argument('--no-sandbox')
                options.add_argument('--disable-dev-shm-usage')
                self._driver = Chrome(options=options, version_main=146)
            except Exception as e:
                print(f"  [Wellfound] Failed to init browser: {e}")
        return self._driver

    def scrape_company(self, company_url: str, company_name: str) -> List[Dict]:
        return self.scrape_search(company_name)

    def scrape_search(self, query: str, location: str = None) -> List[Dict]:
        """Search Wellfound for jobs"""
        slug = query.lower().replace(' ', '-')
        url = f"https://wellfound.com/role/l/{slug}"
        print(f"  [Wellfound] Searching for '{query}'")

        # Try HTTP first
        html = None
        response = self._safe_get(url)
        if response and response.status_code == 200:
            html = response.text
        else:
            # Fallback: use Selenium
            print(f"  [Wellfound] HTTP blocked, trying browser fallback...")
            driver = self._get_driver()
            if driver:
                try:
                    driver.get(url)
                    time.sleep(4)
                    # Scroll to load more
                    for _ in range(3):
                        driver.execute_script("window.scrollBy(0, 1000)")
                        time.sleep(1)
                    html = driver.page_source
                except Exception as e:
                    print(f"  [Wellfound] Browser error: {e}")

        if not html:
            return []

        return self._parse_html(html, query)

    def _parse_html(self, html: str, query: str) -> List[Dict]:
        """Parse Wellfound HTML for job listings"""
        jobs = []
        try:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html, 'html.parser')

            # Wellfound uses various class patterns for job cards
            selectors = [
                '[class*="styles_result"]',
                '[class*="job-listing"]',
                '[data-test="StartupResult"]',
                '.mb-6 > div[class*="w-full"]',
                'a[href*="/jobs/"]',
            ]

            cards = []
            for sel in selectors:
                cards = soup.select(sel)
                if len(cards) >= 2:
                    break

            # Also try finding all job links
            if len(cards) < 2:
                all_links = soup.find_all('a', href=True)
                job_links = [l for l in all_links if '/jobs/' in l.get('href', '') and l.get_text(strip=True)]
                if job_links:
                    cards = job_links

            seen = set()
            for card in cards[:50]:
                title = ''
                company = ''
                location = 'Remote'
                url = ''

                if card.name == 'a':
                    title = card.get_text(strip=True)
                    url = card.get('href', '')
                else:
                    title_el = card.select_one('h2, h3, a, [class*="title"]')
                    if title_el:
                        title = title_el.get_text(strip=True)
                        if title_el.name == 'a':
                            url = title_el.get('href', '')

                    company_el = card.select_one('[class*="company"], [class*="startup"]')
                    if company_el:
                        company = company_el.get_text(strip=True)

                    loc_el = card.select_one('[class*="location"]')
                    if loc_el:
                        location = loc_el.get_text(strip=True)

                if not title or len(title) < 3 or title.lower() in seen:
                    continue
                seen.add(title.lower())

                if url and not url.startswith('http'):
                    url = f"https://wellfound.com{url}"
                if not url:
                    url = f"https://wellfound.com/role/l/{query.lower().replace(' ', '-')}"

                raw = {
                    'id': '', 'title': title[:150], 'company': company or 'Wellfound',
                    'location': location, 'url': url, 'description': '', 'posted_date': '',
                }
                jobs.append(self._normalize_job(raw, source='wellfound', ats='wellfound', company_name=company or 'Wellfound'))

        except ImportError:
            print("  [Wellfound] BeautifulSoup not installed")
        except Exception as e:
            print(f"  [Wellfound] Parse error: {e}")

        print(f"  [Wellfound] Found {len(jobs)} jobs")
        self._rate_limit()
        return jobs

    def __del__(self):
        if self._driver:
            try:
                self._driver.quit()
            except:
                pass
