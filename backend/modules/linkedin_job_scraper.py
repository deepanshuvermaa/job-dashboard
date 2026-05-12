"""
LinkedIn Job Scraper using Selenium
"""

import time
import re
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, NoSuchElementException
try:
    from undetected_chromedriver import Chrome, ChromeOptions
except ImportError:
    Chrome = None
    ChromeOptions = None
    print("[WARN] undetected_chromedriver not available, using standard selenium")
from typing import List, Dict, Optional
import os
from core.config import settings

def parse_posted_days(date_string: str) -> int:
    """Convert 'Posted 3 days ago' to integer days"""
    if not date_string:
        return None

    date_lower = date_string.lower()
    nums = re.findall(r'\d+', date_string)

    if 'hour' in date_lower or 'minute' in date_lower or 'just now' in date_lower:
        return 0
    elif 'day' in date_lower:
        return int(nums[0]) if nums else 1
    elif 'week' in date_lower:
        weeks = int(nums[0]) if nums else 1
        return weeks * 7
    elif 'month' in date_lower:
        months = int(nums[0]) if nums else 1
        return months * 30
    elif 'year' in date_lower:
        years = int(nums[0]) if nums else 1
        return years * 365
    else:
        return None

class LinkedInJobScraper:
    def __init__(self, email: str = None, password: str = None, headless: bool = False):
        self.email = email or settings.LINKEDIN_EMAIL
        self.password = password or settings.LINKEDIN_PASSWORD
        self.headless = headless
        self.driver = None
        self.logged_in = False

    def _init_driver(self):
        """Initialize Chrome with stealth mode using webdriver-manager (auto-downloads correct chromedriver)."""
        from selenium import webdriver
        from selenium.webdriver.chrome.service import Service
        from selenium.webdriver.chrome.options import Options
        from webdriver_manager.chrome import ChromeDriverManager
        from selenium_stealth import stealth

        options = Options()
        if self.headless:
            options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)

        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=options)

        stealth(self.driver,
                languages=["en-US", "en"],
                vendor="Google Inc.",
                platform="Win32",
                webgl_vendor="Intel Inc.",
                renderer="Intel Iris OpenGL Engine",
                fix_hairline=True)

        self.driver.maximize_window()

    def login(self) -> bool:
        """Login to LinkedIn with 2FA/checkpoint support"""
        try:
            if not self.driver:
                self._init_driver()

            # Check if already logged in from persistent profile
            print("Checking if already logged in...")
            self.driver.get('https://www.linkedin.com/feed/')

            # Wait up to 15 seconds for the page to fully load
            for wait in range(15):
                time.sleep(1)
                current_url = self.driver.current_url
                if '/feed' in current_url or '/mynetwork' in current_url:
                    try:
                        self.driver.find_element(By.ID, 'global-nav')
                        print("Already logged in from saved session!")
                        self.logged_in = True
                        return True
                    except:
                        pass
                # If redirected to login page, break and do fresh login
                if '/login' in current_url or '/uas/' in current_url:
                    print("Not logged in, redirected to login page")
                    break

            # Double check — maybe the feed loaded but global-nav ID changed
            current_url = self.driver.current_url
            if '/feed' in current_url:
                # We're on the feed — must be logged in even if we can't find global-nav
                print("On feed page — treating as logged in!")
                self.logged_in = True
                return True

            # Not logged in — do fresh login
            print("Navigating to LinkedIn login...")
            self.driver.get('https://www.linkedin.com/login')
            time.sleep(2)

            # Enter email
            email_field = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, 'username'))
            )
            email_field.clear()
            email_field.send_keys(self.email)

            # Enter password
            password_field = self.driver.find_element(By.ID, 'password')
            password_field.clear()
            password_field.send_keys(self.password)

            # Click login
            login_button = self.driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
            login_button.click()

            # Wait for either dashboard OR checkpoint/2FA page
            print("Waiting for login result (will wait up to 90s for 2FA approval)...")
            checkpoint_seen = False
            for i in range(90):
                time.sleep(1)
                current_url = self.driver.current_url

                # Success — landed on feed/dashboard
                if '/feed' in current_url or '/mynetwork' in current_url or '/jobs' in current_url:
                    try:
                        self.driver.find_element(By.ID, 'global-nav')
                        print("Successfully logged in to LinkedIn!")
                        self.logged_in = True
                        return True
                    except:
                        pass

                # Still on checkpoint — user needs to approve on phone
                if 'checkpoint' in current_url or 'challenge' in current_url:
                    if not checkpoint_seen:
                        checkpoint_seen = True
                        print("  2FA checkpoint detected — approve on your LinkedIn mobile app...")

                    # Every 5 seconds, try force-navigating to feed to check if approved
                    if i > 10 and i % 5 == 0:
                        print(f"  Checking if 2FA was approved... ({90 - i}s remaining)")
                        self.driver.get('https://www.linkedin.com/feed/')
                        time.sleep(2)
                        check_url = self.driver.current_url
                        if '/feed' in check_url:
                            try:
                                self.driver.find_element(By.ID, 'global-nav')
                                print("2FA approved! Successfully logged in!")
                                self.logged_in = True
                                return True
                            except:
                                pass
                        # If still redirected to checkpoint, keep waiting
                    continue

                # Security verification
                if 'security' in current_url:
                    if i % 10 == 0:
                        print(f"  Security verification — complete it in the browser... ({90 - i}s remaining)")
                    continue

            # Final force-navigate attempt
            print("Final login check...")
            self.driver.get('https://www.linkedin.com/feed/')
            time.sleep(3)
            if '/feed' in self.driver.current_url:
                print("Successfully logged in to LinkedIn!")
                self.logged_in = True
                return True

            print("Login timed out — 2FA was not approved within 90 seconds")
            return False

        except Exception as e:
            print(f"Login failed: {e}")
            return False

    def _build_search_url(
        self,
        keywords: str,
        location: str = "United States",
        job_type: str = None,
        experience_level: str = None,
        easy_apply: bool = False,
        remote: bool = False,
        posted_within: str = None,
        sort_by: str = "DD",
        start: int = 0
    ) -> str:
        """Build LinkedIn search URL with all filters and pagination"""
        # LinkedIn geoId mapping — text-only location is unreliable for country-level searches
        GEO_IDS = {
            "india": "102713980",
            "united states": "103644278",
            "usa": "103644278",
            "us": "103644278",
            "united kingdom": "101165590",
            "uk": "101165590",
            "canada": "101174742",
            "australia": "101452733",
            "germany": "101282230",
            "singapore": "102454443",
            "remote": None,  # no geoId for remote — use f_WT=2
            # Indian cities
            "bangalore": "105214831",
            "bengaluru": "105214831",
            "mumbai": "102717819",
            "hyderabad": "102562005",
            "pune": "115524",
            "delhi": "102713980",
            "gurgaon": "102713980",
            "noida": "102713980",
            "chennai": "102572908",
        }
        from urllib.parse import quote
        encoded_kw = quote(keywords)
        search_url = f"https://www.linkedin.com/jobs/search/?keywords={encoded_kw}"

        if location:
            loc_lower = location.lower().strip()
            geo_id = GEO_IDS.get(loc_lower)
            if geo_id:
                search_url += f"&geoId={geo_id}&location={quote(location)}"
            elif loc_lower == "remote":
                pass  # handled by f_WT below
            else:
                search_url += f"&location={quote(location)}"
        if easy_apply:
            search_url += "&f_AL=true"
        if remote or (location and location.lower().strip() == "remote"):
            search_url += "&f_WT=2"

        # Job type filters
        job_type_map = {
            'full-time': 'F',
            'part-time': 'P',
            'contract': 'C',
            'internship': 'I'
        }
        if job_type and job_type in job_type_map:
            search_url += f"&f_JT={job_type_map[job_type]}"

        # Experience level filters — f_E accepts comma-separated values
        exp_map = {
            'internship': '1',
            'entry': '2',
            'associate': '3',
            'mid': '3',
            'senior': '4',
            'director': '5',
            'executive': '6',
            'entry_associate': '1,2,3',  # 0-3 years
        }
        if experience_level and experience_level in exp_map:
            search_url += f"&f_E={exp_map[experience_level]}"

        # Posted time filter (f_TPR) — accepts preset or custom hours
        time_map = {
            '1h': 'r3600',
            '6h': 'r21600',
            '10h': 'r36000',
            '12h': 'r43200',
            '24h': 'r86400',
            'week': 'r604800',
            'month': 'r2592000'
        }
        if posted_within:
            if posted_within in time_map:
                search_url += f"&f_TPR={time_map[posted_within]}"
            elif posted_within.endswith('h') and posted_within[:-1].isdigit():
                # Custom hours like "3h", "8h", "15h"
                seconds = int(posted_within[:-1]) * 3600
                search_url += f"&f_TPR=r{seconds}"
            elif posted_within.startswith('r'):
                # Raw seconds like "r36000"
                search_url += f"&f_TPR={posted_within}"

        # Sort by date (most recent first)
        if sort_by:
            search_url += f"&sortBy={sort_by}"

        # Pagination parameter
        if start > 0:
            search_url += f"&start={start}"

        return search_url

    def search_jobs(
        self,
        keywords: str,
        location: str = "United States",
        job_type: str = None,
        experience_level: str = None,
        easy_apply: bool = False,
        remote: bool = False,
        max_results: int = 100,
        posted_within: str = None
    ) -> List[Dict]:
        """Search for jobs on LinkedIn using URL-based pagination (no scroll limit)"""
        try:
            if not self.logged_in:
                if not self.login():
                    return []

            jobs = []
            seen_urls = set()
            page_size = 25  # LinkedIn returns 25 jobs per page
            max_pages = (max_results + page_size - 1) // page_size  # Ceiling division
            empty_pages = 0
            max_empty_pages = 2  # Stop after 2 consecutive empty pages

            # Updated selectors for LinkedIn 2024/2025
            selectors = [
                'ul.scaffold-layout__list-container li',
                'ul.jobs-search__results-list li',
                'div.jobs-search-results__list-item',
                '.scaffold-layout__list-item'
            ]

            print(f"Target: {max_results} jobs across up to {max_pages} pages")

            for page in range(max_pages):
                if len(jobs) >= max_results:
                    break

                start = page * page_size
                page_url = self._build_search_url(
                    keywords=keywords,
                    location=location,
                    job_type=job_type,
                    experience_level=experience_level,
                    easy_apply=easy_apply,
                    remote=remote,
                    posted_within=posted_within,
                    start=start
                )

                print(f"\n--- Page {page + 1} (start={start}) ---")
                print(f"URL: {page_url}")
                self.driver.get(page_url)

                # Randomized wait to mimic human behavior
                time.sleep(random.uniform(4, 7))

                # Scroll the job list container to load all lazy-loaded cards
                for scroll_pass in range(8):
                    self.driver.execute_script("""
                        const container = document.querySelector('.jobs-search-results-list')
                            || document.querySelector('.scaffold-layout__list-container')
                            || document.querySelector('.jobs-search__results-list');
                        if (container) {
                            container.scrollTop = container.scrollHeight;
                        }
                        window.scrollBy(0, 800);
                    """)
                    time.sleep(random.uniform(0.5, 1.0))
                # Scroll back to top to stabilize
                self.driver.execute_script("window.scrollTo(0, 0);")
                time.sleep(0.5)

                # Find job cards on this page
                job_cards = []
                for selector in selectors:
                    job_cards = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if job_cards:
                        break

                if not job_cards:
                    print(f"No job cards found on page {page + 1}")
                    empty_pages += 1
                    if empty_pages >= max_empty_pages:
                        print(f"Stopping: {max_empty_pages} consecutive empty pages")
                        break
                    continue

                empty_pages = 0  # Reset counter on successful page
                print(f"Found {len(job_cards)} cards on page {page + 1}")

                # Extract jobs from this page
                page_jobs = 0
                for i, card in enumerate(job_cards):
                    if len(jobs) >= max_results:
                        break
                    try:
                        job = self._extract_job_info(card, start + i)
                        if job and job.get('job_url') not in seen_urls:
                            seen_urls.add(job.get('job_url'))
                            jobs.append(job)
                            page_jobs += 1
                            print(f"  [{len(jobs)}/{max_results}] {job['title']} at {job['company']}")
                    except Exception as e:
                        print(f"  Error extracting job {start + i}: {e}")
                        continue

                print(f"Page {page + 1}: extracted {page_jobs} new jobs (total: {len(jobs)})")

                # If page returned fewer than expected, we may be near the end
                if len(job_cards) < page_size // 2:
                    print(f"Partial page ({len(job_cards)} < {page_size // 2}), likely last page")
                    break

                # Anti-rate-limit delay between pages
                if page < max_pages - 1 and len(jobs) < max_results:
                    delay = random.uniform(2, 5)
                    print(f"Waiting {delay:.1f}s before next page...")
                    time.sleep(delay)

            print(f"\nTotal jobs found: {len(jobs)}")
            # Tag all jobs with source and timestamp
            from datetime import datetime as dt
            now = dt.now().isoformat()
            for job in jobs:
                job['source'] = 'linkedin'
                job['scraped_at'] = now
            return jobs

        except Exception as e:
            print(f"Error searching jobs: {e}")
            return []

    def search_jobs_multi(
        self,
        queries: List[str],
        location: str = "United States",
        max_results_per_query: int = 50,
        **kwargs
    ) -> List[Dict]:
        """Run multiple search queries and deduplicate results across all queries"""
        all_jobs = {}
        total_dupes = 0

        print(f"\n{'='*60}")
        print(f"MULTI-QUERY SEARCH: {len(queries)} queries, {max_results_per_query} per query")
        print(f"{'='*60}")

        for i, query in enumerate(queries):
            print(f"\n--- Query {i + 1}/{len(queries)}: '{query}' ---")
            jobs = self.search_jobs(
                keywords=query,
                location=location,
                max_results=max_results_per_query,
                **kwargs
            )

            new_count = 0
            for job in jobs:
                key = job.get('job_url', '') or job.get('id', '')
                if key and key not in all_jobs:
                    all_jobs[key] = job
                    new_count += 1
                else:
                    total_dupes += 1

            print(f"Query '{query}': {len(jobs)} found, {new_count} new, {len(jobs) - new_count} duplicates")

            # Delay between queries
            if i < len(queries) - 1:
                delay = random.uniform(5, 10)
                print(f"Waiting {delay:.1f}s before next query...")
                time.sleep(delay)

        print(f"\n{'='*60}")
        print(f"MULTI-QUERY RESULTS: {len(all_jobs)} unique jobs, {total_dupes} duplicates skipped")
        print(f"{'='*60}")

        return list(all_jobs.values())

    def _extract_job_info(self, card, index: int = 0) -> Optional[Dict]:
        """Extract job information from a job card"""
        try:
            # Click on job card to load details
            card.click()
            time.sleep(3)  # Increased wait time for details to load

            # Try multiple selectors for title (LinkedIn updates these frequently)
            title = None
            title_selectors = [
                '.job-card-list__title',
                'a.job-card-container__link',
                '.scaffold-layout__list-item h3',
                '.artdeco-entity-lockup__title',
                'h3.t-bold span[aria-hidden="true"]'
            ]
            for sel in title_selectors:
                try:
                    title_elem = card.find_element(By.CSS_SELECTOR, sel)
                    title = title_elem.text.strip()
                    if title:
                        break
                except:
                    continue

            if not title:
                # Fallback: get any text from the card
                title = card.text.split('\n')[0][:100]

            # Company name selectors
            company = None
            company_selectors = [
                '.job-card-container__company-name',
                '.artdeco-entity-lockup__subtitle',
                'span.job-card-container__primary-description',
                '.job-card-container__metadata-wrapper span'
            ]
            for sel in company_selectors:
                try:
                    company_elem = card.find_element(By.CSS_SELECTOR, sel)
                    company = company_elem.text.strip()
                    if company:
                        break
                except:
                    continue

            if not company:
                company = "Company Not Listed"

            # Location selectors
            location = None
            location_selectors = [
                '.job-card-container__metadata-item',
                'li.job-card-container__metadata-item',
                '.artdeco-entity-lockup__caption'
            ]
            for sel in location_selectors:
                try:
                    loc_elem = card.find_element(By.CSS_SELECTOR, sel)
                    location = loc_elem.text.strip()
                    if location:
                        break
                except:
                    continue

            if not location:
                location = "Location Not Specified"

            # Get job URL
            link = None
            try:
                link_elem = card.find_element(By.CSS_SELECTOR, 'a')
                link = link_elem.get_attribute('href')
                if link:
                    # Clean up URL (remove tracking params)
                    if '?' in link:
                        link = link.split('?')[0]
            except:
                link = "#"

            job_id = link.split('/')[-2] if '/' in link and link != "#" else f"job_{index}"

            # Check for Easy Apply button (ENHANCED - actually verify button exists)
            easy_apply = False

            # Strategy 1: Check for Easy Apply badge in card
            easy_apply_badge_selectors = [
                '.job-card-container__apply-method',
                'li-icon[type="job-posting-easy-apply"]',
                '.artdeco-inline-feedback--success'
            ]
            for sel in easy_apply_badge_selectors:
                if len(card.find_elements(By.CSS_SELECTOR, sel)) > 0:
                    easy_apply = True
                    break

            # Strategy 2: Check for Easy Apply button in details panel (more reliable)
            if not easy_apply:
                try:
                    easy_apply_button_selectors = [
                        'button[aria-label*="Easy Apply"]',
                        'button.jobs-apply-button--top-card',
                        '.jobs-apply-button'
                    ]
                    for btn_sel in easy_apply_button_selectors:
                        buttons = self.driver.find_elements(By.CSS_SELECTOR, btn_sel)
                        for button in buttons:
                            button_text = button.text.lower() if button.text else ''
                            button_label = button.get_attribute('aria-label') or ''
                            button_label_lower = button_label.lower()
                            if 'easy apply' in button_text or 'easy apply' in button_label_lower:
                                easy_apply = True
                                print(f"  [EASY APPLY DETECTED] {title}")
                                break
                        if easy_apply:
                            break
                except Exception as e:
                    pass

            # Get description from details panel (right side)
            description = title
            try:
                desc_selectors = [
                    '.jobs-description__content',
                    '.jobs-description-content__text',
                    '#job-details'
                ]
                for sel in desc_selectors:
                    try:
                        desc_elem = self.driver.find_element(By.CSS_SELECTOR, sel)
                        description = desc_elem.text[:500]
                        if description:
                            break
                    except:
                        continue
            except:
                pass

            # Try to get posted date - Enhanced extraction from details panel
            posted_date = "Recently"
            posted_days_ago = None
            try:
                # First try: job card time element
                time_elem = card.find_element(By.CSS_SELECTOR, 'time')
                posted_date = time_elem.get_attribute('datetime') or time_elem.text
                posted_days_ago = parse_posted_days(posted_date)
            except:
                # Second try: job details panel (right side)
                try:
                    details_time_selectors = [
                        '.job-details-jobs-unified-top-card__posted-date',
                        '.jobs-unified-top-card__subtitle-primary-grouping time',
                        '.jobs-unified-top-card__job-insight span',
                        'span.tvm__text'
                    ]
                    for sel in details_time_selectors:
                        try:
                            time_elem = self.driver.find_element(By.CSS_SELECTOR, sel)
                            posted_text = time_elem.text.strip()
                            if posted_text and ('ago' in posted_text.lower() or 'hour' in posted_text.lower() or 'day' in posted_text.lower()):
                                posted_date = posted_text
                                posted_days_ago = parse_posted_days(posted_text)
                                break
                        except:
                            continue
                except:
                    pass

            # Extract "People Who Can Help" - recruiters and connections
            people_who_can_help = self._extract_people_who_can_help()

            # Extract hiring team/recruiter info
            recruiter_info = self._extract_recruiter_info()

            # Get salary if available
            salary = None
            try:
                salary_elem = self.driver.find_element(By.CSS_SELECTOR, '.job-details-jobs-unified-top-card__job-insight span')
                salary = salary_elem.text
            except:
                pass

            # Get applicant count
            applicant_count = None
            try:
                applicants_elem = self.driver.find_element(By.CSS_SELECTOR, '.num-applicants__caption')
                applicant_count = applicants_elem.text
            except:
                pass

            # Get company size, industry
            company_details = self._extract_company_details()

            # Calculate relevance score based on job match
            relevance_score = self._calculate_relevance(title, description, easy_apply)

            return {
                'id': job_id,
                'title': title,
                'company': company,
                'location': location,
                'job_url': link,
                'easy_apply': easy_apply,
                'job_type': 'full-time',
                'experience_level': 'mid',
                'description_snippet': description,
                'posted_date': posted_date,
                'posted_days_ago': posted_days_ago,
                'salary': salary,
                'applicant_count': applicant_count,
                'relevance_score': relevance_score,
                'people_who_can_help': people_who_can_help,
                'recruiter_info': recruiter_info,
                'company_details': company_details
            }

        except Exception as e:
            print(f"Error extracting job info: {e}")
            return None

    def _calculate_relevance(self, title: str, description: str, easy_apply: bool) -> float:
        """Calculate job relevance score based on multiple factors"""
        score = 0.5  # Base score

        # Easy Apply jobs get +0.2
        if easy_apply:
            score += 0.2

        # Check for seniority keywords in title
        title_lower = title.lower()
        if any(word in title_lower for word in ['senior', 'lead', 'principal', 'staff']):
            score += 0.1
        elif any(word in title_lower for word in ['junior', 'entry', 'fresher', 'intern']):
            score += 0.05

        # Check for tech stack matches in description
        tech_keywords = ['python', 'react', 'javascript', 'node', 'sql', 'aws', 'docker', 'kubernetes']
        desc_lower = description.lower()
        matches = sum(1 for keyword in tech_keywords if keyword in desc_lower)
        score += min(matches * 0.05, 0.2)  # Max 0.2 bonus

        # Cap at 0.99 (never 100%)
        return min(score, 0.99)

    def _extract_people_who_can_help(self) -> List[Dict]:
        """Extract People Who Can Help section - recruiters and connections at company"""
        people = []
        try:
            # Look for the specific component you mentioned
            people_section_selectors = [
                '[data-sdui-component="com.linkedin.sdui.generated.jobseeker.dsl.impl.peopleWhoCanHelp"]',
                '.job-details-hiring-team',
                '.hiring-team__members'
            ]

            people_section = None
            for selector in people_section_selectors:
                try:
                    people_section = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if people_section:
                        print(f"Found People Who Can Help section")
                        break
                except:
                    continue

            if not people_section:
                return []

            # Extract individual people cards
            person_cards = people_section.find_elements(By.CSS_SELECTOR, '.artdeco-entity-lockup, .hiring-team__member-item')

            for person_card in person_cards[:10]:  # Limit to 10 people
                try:
                    # Get person name
                    name = person_card.find_element(By.CSS_SELECTOR, '.artdeco-entity-lockup__title, .hiring-team__member-name').text

                    # Get person title/role
                    title = person_card.find_element(By.CSS_SELECTOR, '.artdeco-entity-lockup__subtitle, .hiring-team__member-title').text

                    # Get profile URL and DM link
                    profile_link = person_card.find_element(By.CSS_SELECTOR, 'a').get_attribute('href')

                    # Generate DM link (LinkedIn messaging URL)
                    dm_link = None
                    if '/in/' in profile_link:
                        profile_id = profile_link.split('/in/')[1].split('/')[0].split('?')[0]
                        dm_link = f"https://www.linkedin.com/messaging/compose/?recipient={profile_id}"

                    # Try to get connection degree
                    connection_degree = None
                    try:
                        degree_elem = person_card.find_element(By.CSS_SELECTOR, '.dist-value')
                        connection_degree = degree_elem.text
                    except:
                        pass

                    people.append({
                        'name': name,
                        'title': title,
                        'profile_url': profile_link,
                        'dm_link': dm_link,
                        'connection_degree': connection_degree
                    })

                    print(f"✓ Found: {name} - {title}")

                except Exception as e:
                    print(f"Error extracting person: {e}")
                    continue

        except Exception as e:
            print(f"Error in _extract_people_who_can_help: {e}")

        return people

    def _extract_recruiter_info(self) -> Dict:
        """Extract recruiter/hiring manager information - ENHANCED VERSION"""
        recruiter = {}
        try:
            # Scroll down slightly to load recruiter section
            self.driver.execute_script("window.scrollBy(0, 400);")
            time.sleep(1)

            # Multiple selector strategies for recruiter
            recruiter_strategies = [
                # Strategy 1: Job poster name (most common)
                {
                    'container': '.jobs-poster__name',
                    'name': 'a',
                    'link': 'a'
                },
                # Strategy 2: Hiring team member
                {
                    'container': '.hiring-team__member',
                    'name': '.artdeco-entity-lockup__title',
                    'title': '.artdeco-entity-lockup__subtitle',
                    'link': 'a'
                },
                # Strategy 3: Meet the hiring team section
                {
                    'container': '[data-test-job-details-hiring-team] .artdeco-entity-lockup',
                    'name': '.artdeco-entity-lockup__title',
                    'title': '.artdeco-entity-lockup__subtitle',
                    'link': 'a'
                },
                # Strategy 4: Job details top card
                {
                    'container': '.job-details-jobs-unified-top-card__hiring-team',
                    'name': 'a',
                    'link': 'a'
                }
            ]

            for strategy in recruiter_strategies:
                try:
                    container = self.driver.find_element(By.CSS_SELECTOR, strategy['container'])

                    # Extract name
                    name_elem = container.find_element(By.CSS_SELECTOR, strategy['name'])
                    name = name_elem.text.strip()
                    if not name:
                        continue

                    recruiter['name'] = name

                    # Extract title if available
                    if 'title' in strategy:
                        try:
                            title_elem = container.find_element(By.CSS_SELECTOR, strategy['title'])
                            recruiter['title'] = title_elem.text.strip()
                        except:
                            pass

                    # Extract profile link
                    try:
                        link_elem = container.find_element(By.CSS_SELECTOR, strategy['link'])
                        profile_url = link_elem.get_attribute('href')

                        if profile_url and '/in/' in profile_url:
                            recruiter['profile_url'] = profile_url

                            # Generate DM link
                            profile_id = profile_url.split('/in/')[1].split('/')[0].split('?')[0]
                            recruiter['dm_link'] = f"https://www.linkedin.com/messaging/compose/?recipient={profile_id}"
                    except:
                        pass

                    if recruiter.get('name'):
                        print(f"✓ Found recruiter: {recruiter['name']}")
                        return recruiter

                except Exception as e:
                    continue

            # If no recruiter found, try to extract from "About the job" section
            if not recruiter:
                try:
                    # Look for any LinkedIn profile links in the job description
                    links = self.driver.find_elements(By.CSS_SELECTOR, 'a[href*="/in/"]')
                    for link in links[:3]:  # Check first 3 profile links
                        href = link.get_attribute('href')
                        text = link.text.strip()
                        if text and len(text) < 50 and '/in/' in href:  # Likely a person's name
                            recruiter['name'] = text
                            recruiter['profile_url'] = href
                            profile_id = href.split('/in/')[1].split('/')[0].split('?')[0]
                            recruiter['dm_link'] = f"https://www.linkedin.com/messaging/compose/?recipient={profile_id}"
                            print(f"✓ Found recruiter from description: {text}")
                            break
                except:
                    pass

        except Exception as e:
            print(f"Error extracting recruiter: {e}")

        return recruiter

    def _extract_company_details(self) -> Dict:
        """Extract company information"""
        details = {}
        try:
            # Company size
            try:
                size_elem = self.driver.find_element(By.CSS_SELECTOR, '.job-details-jobs-unified-top-card__job-insight--company-size')
                details['company_size'] = size_elem.text
            except:
                pass

            # Industry
            try:
                industry_elem = self.driver.find_element(By.CSS_SELECTOR, '.job-details-jobs-unified-top-card__job-insight--industry')
                details['industry'] = industry_elem.text
            except:
                pass

            # Company LinkedIn URL
            try:
                company_link = self.driver.find_element(By.CSS_SELECTOR, '.jobs-unified-top-card__company-name a')
                details['company_url'] = company_link.get_attribute('href')
            except:
                pass

        except Exception as e:
            print(f"Error extracting company details: {e}")

        return details

    def apply_to_job(self, job_url: str, user_config: Dict = None, use_advanced_bot: bool = True) -> Dict:
        """
        Apply to a job using Easy Apply

        Args:
            job_url: LinkedIn job URL
            user_config: User configuration for form filling
            use_advanced_bot: Whether to use advanced EasyApplyBot (with question answering)

        Returns:
            Dictionary with application result
        """
        try:
            # If advanced bot is requested and config is provided, use EasyApplyBot
            if use_advanced_bot and user_config:
                from .easy_apply_bot import EasyApplyBot
                from .ai_providers import AIProviderManager

                # Initialize AI provider
                ai_config = user_config.get('ai', {})
                ai_manager = AIProviderManager(ai_config)
                ai_client = ai_manager.get_raw_client()

                # Initialize Easy Apply bot with existing driver
                bot = EasyApplyBot(user_config, ai_client)
                bot.driver = self.driver  # Use existing driver

                # Apply using advanced bot
                result = bot.apply_to_job(job_url)
                return result

            # Fallback to simple application (original logic)
            # Ensure driver is initialized
            if not self.driver:
                self._init_driver()

            if not self.logged_in:
                if not self.login():
                    return {'success': False, 'error': 'Login failed'}

            print(f"Navigating to job: {job_url}")
            self.driver.get(job_url)
            time.sleep(3)

            # Try multiple selectors for Easy Apply button
            easy_apply_selectors = [
                'button[aria-label*="Easy Apply"]',
                'button.jobs-apply-button',
                'button:has-text("Easy Apply")',
                '.jobs-apply-button--top-card button'
            ]

            easy_apply_button = None
            for selector in easy_apply_selectors:
                try:
                    easy_apply_button = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                    )
                    if easy_apply_button:
                        print(f"Found Easy Apply button with selector: {selector}")
                        break
                except:
                    continue

            if not easy_apply_button:
                print("Easy Apply button not found")
                return {'success': False, 'error': 'Easy Apply not available'}

            easy_apply_button.click()
            time.sleep(2)

            # Handle multi-step application form
            max_steps = 10
            for step in range(max_steps):
                print(f"Processing step {step + 1}...")

                # Check for required fields and fill them
                try:
                    # Phone number field
                    phone_inputs = self.driver.find_elements(By.CSS_SELECTOR, 'input[type="text"][id*="phoneNumber"]')
                    for phone_input in phone_inputs:
                        if not phone_input.get_attribute('value'):
                            phone_number = user_config.get('phone', '+1234567890') if user_config else '+1234567890'
                            phone_input.send_keys(phone_number)
                            print("Filled phone number")
                except:
                    pass

                # Look for Next button
                next_button = None
                next_selectors = [
                    'button[aria-label="Continue to next step"]',
                    'button[aria-label*="Next"]',
                    'button:has-text("Next")',
                    'footer button[aria-label*="Continue"]'
                ]

                for selector in next_selectors:
                    try:
                        next_button = self.driver.find_element(By.CSS_SELECTOR, selector)
                        if next_button and next_button.is_enabled():
                            break
                    except:
                        continue

                if next_button and next_button.is_enabled():
                    print("Clicking Next...")
                    next_button.click()
                    time.sleep(2)
                    continue

                # No next button, try submit
                submit_button = None
                submit_selectors = [
                    'button[aria-label="Submit application"]',
                    'button[aria-label*="Submit"]',
                    'button:has-text("Submit")',
                    'footer button[type="submit"]'
                ]

                for selector in submit_selectors:
                    try:
                        submit_button = self.driver.find_element(By.CSS_SELECTOR, selector)
                        if submit_button and submit_button.is_enabled():
                            break
                    except:
                        continue

                if submit_button and submit_button.is_enabled():
                    print("Clicking Submit...")
                    submit_button.click()
                    time.sleep(2)
                    print(f"✓ Successfully applied to job!")
                    return {'success': True, 'job_url': job_url}

                # Neither next nor submit found
                print("No next or submit button found, ending")
                break

            return {'success': False, 'error': 'Could not complete application'}

        except Exception as e:
            print(f"Error applying to job: {e}")
            return {'success': False, 'error': str(e)}

    def close(self):
        """Close the browser"""
        if self.driver:
            self.driver.quit()
