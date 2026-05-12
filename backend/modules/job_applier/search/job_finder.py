"""Find jobs on LinkedIn"""
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from backend.core.browser.stealth_browser import StealthBrowser, HumanBehavior
from backend.core.browser.session_manager import SessionManager
from typing import List, Dict
import time

class JobFinder:
    """Search for jobs on LinkedIn"""

    def __init__(self, user_id: str):
        self.user_id = user_id
        self.session_manager = SessionManager(user_id)
        self.driver = None

    async def search_jobs(
        self,
        keywords: str,
        location: str = "United States",
        easy_apply_only: bool = True,
        max_results: int = 30
    ) -> List[Dict]:
        """
        Search for jobs

        Returns list of job dictionaries
        """
        jobs = []

        try:
            self.driver = StealthBrowser.create(headless=False, use_profile=True)

            # Load session
            if not self.session_manager.load_cookies(self.driver):
                print("⚠️  Please log in to LinkedIn manually...")
                return []

            # Build search URL
            search_url = f"https://www.linkedin.com/jobs/search/?keywords={keywords.replace(' ', '%20')}"
            search_url += f"&location={location.replace(' ', '%20')}"

            if easy_apply_only:
                search_url += "&f_AL=true"  # Easy Apply filter

            self.driver.get(search_url)
            HumanBehavior.random_delay(3, 5)

            # Scroll to load jobs
            for _ in range(3):
                HumanBehavior.smooth_scroll(self.driver)
                HumanBehavior.random_delay(2, 3)

            # Find job cards
            job_cards = self.driver.find_elements(By.CLASS_NAME, "job-card-container")

            for card in job_cards[:max_results]:
                try:
                    job = self._extract_job_data(card)
                    if job:
                        jobs.append(job)
                except:
                    continue

            # Save session
            self.session_manager.save_cookies(self.driver)

            return jobs

        except Exception as e:
            print(f"Error searching jobs: {e}")
            return []

        finally:
            if self.driver:
                self.driver.quit()

    def _extract_job_data(self, card) -> Dict:
        """Extract job data from card"""
        try:
            # Title
            title_elem = card.find_element(By.CLASS_NAME, "job-card-list__title")
            title = title_elem.text.strip()

            # Company
            company_elem = card.find_element(By.CLASS_NAME, "job-card-container__primary-description")
            company = company_elem.text.strip()

            # Location
            try:
                location_elem = card.find_element(By.CLASS_NAME, "job-card-container__metadata-item")
                location = location_elem.text.strip()
            except:
                location = "Remote"

            # Link
            link = card.find_element(By.TAG_NAME, "a").get_attribute("href")

            # Job ID from link
            job_id = link.split("/")[-2] if "/" in link else link

            return {
                'linkedin_job_id': job_id,
                'title': title,
                'company': company,
                'location': location,
                'job_url': link,
                'source': 'linkedin'
            }

        except Exception as e:
            return None
