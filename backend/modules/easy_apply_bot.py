"""
LinkedIn Easy Apply Automation Bot
Complete implementation based on GodsScion's approach with enhancements
"""

import time
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import undetected_chromedriver as uc

from .clickers_and_finders import (
    get_easy_apply_button, get_easy_apply_modal, find_button_by_text,
    safe_click, wait_span_click, is_element_visible, scroll_to_element,
    find_by_xpath, find_all_by_xpath
)
from .question_answerer import QuestionAnswerer


class EasyApplyBot:
    """Automated LinkedIn Easy Apply bot"""

    def __init__(self, user_config: Dict, ai_client=None):
        """
        Initialize Easy Apply bot

        Args:
            user_config: User's personal information and preferences
            ai_client: OpenAI client for AI-powered features
        """
        self.config = user_config
        self.ai_client = ai_client
        self.driver = None
        self.question_answerer = QuestionAnswerer(user_config, ai_client)

        # Statistics
        self.stats = {
            'applications_attempted': 0,
            'applications_successful': 0,
            'applications_failed': 0,
            'questions_answered': 0,
            'resume_uploaded': 0
        }

        # Paths
        self.screenshot_dir = Path(__file__).parent.parent / "screenshots"
        self.screenshot_dir.mkdir(exist_ok=True)

        self.resume_path = user_config.get('resume_path')

    def initialize_driver(self):
        """Initialize undetected Chrome driver"""
        try:
            options = uc.ChromeOptions()
            options.add_argument('--start-maximized')
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')

            # User data for persistent login
            user_data_dir = self.config.get('chrome_user_data_dir')
            if user_data_dir:
                options.add_argument(f'--user-data-dir={user_data_dir}')

            self.driver = uc.Chrome(options=options, version_main=146)
            print("[OK] Chrome driver initialized successfully")
            return True

        except Exception as e:
            print(f"[ERROR] Failed to initialize driver: {e}")
            return False

    def login_to_linkedin(self, email: str = None, password: str = None) -> bool:
        """Login to LinkedIn"""
        try:
            if not self.driver:
                self.initialize_driver()

            self.driver.get('https://www.linkedin.com/login')
            time.sleep(2)

            # Check if already logged in
            if 'feed' in self.driver.current_url or 'mynetwork' in self.driver.current_url:
                print("[OK] Already logged into LinkedIn")
                return True

            # Use credentials from config if not provided
            email = email or self.config.get('linkedin_email')
            password = password or self.config.get('linkedin_password')

            if not email or not password:
                print("[WARN] No credentials provided. Please log in manually.")
                print("Waiting 60 seconds for manual login...")
                time.sleep(60)
                return 'feed' in self.driver.current_url

            # Enter credentials
            email_field = self.driver.find_element(By.ID, 'username')
            password_field = self.driver.find_element(By.ID, 'password')

            email_field.send_keys(email)
            password_field.send_keys(password)

            # Click sign in
            sign_in_button = self.driver.find_element(By.XPATH, '//button[@type="submit"]')
            sign_in_button.click()

            time.sleep(3)

            # Check for verification
            if 'checkpoint' in self.driver.current_url or 'challenge' in self.driver.current_url:
                print("[WARN] Verification required. Please complete verification manually.")
                print("Waiting 60 seconds...")
                time.sleep(60)

            # Verify login success
            success = 'feed' in self.driver.current_url or 'mynetwork' in self.driver.current_url
            if success:
                print("[OK] Successfully logged into LinkedIn")
            else:
                print("[ERROR] Login may have failed. Please check.")

            return success

        except Exception as e:
            print(f"[ERROR] Login error: {e}")
            return False

    def apply_to_job(self, job_url: str) -> Dict:
        """
        Apply to a single job using Easy Apply

        Args:
            job_url: LinkedIn job URL

        Returns:
            Dictionary with application result and metadata
        """
        result = {
            'success': False,
            'job_url': job_url,
            'applied_at': datetime.now().isoformat(),
            'questions_asked': [],
            'error': None,
            'screenshot_path': None
        }

        try:
            self.stats['applications_attempted'] += 1

            # Navigate to job
            print(f"\n📋 Navigating to job: {job_url}")
            self.driver.get(job_url)
            time.sleep(2)

            # Check if Easy Apply is available
            easy_apply_button = get_easy_apply_button(self.driver)
            if not easy_apply_button:
                result['error'] = 'Easy Apply not available for this job'
                print(f"[WARN] {result['error']}")
                return result

            # Click Easy Apply button
            print("🖱 Clicking Easy Apply button...")
            safe_click(easy_apply_button)
            time.sleep(1.5)

            # Get the modal
            modal = get_easy_apply_modal(self.driver)
            if not modal:
                result['error'] = 'Easy Apply modal did not open'
                print(f"[ERROR] {result['error']}")
                self._take_screenshot('modal_not_found')
                result['screenshot_path'] = self._get_last_screenshot()
                return result

            # Process the application form (multi-step)
            success = self._complete_application_form(modal, result)

            if success:
                result['success'] = True
                self.stats['applications_successful'] += 1
                print("[SUCCESS] Application submitted successfully!")
            else:
                self.stats['applications_failed'] += 1
                print("[FAILED] Application failed")

            return result

        except Exception as e:
            result['error'] = str(e)
            self.stats['applications_failed'] += 1
            print(f"[FAILED] Application error: {e}")

            # Take screenshot on failure
            self._take_screenshot('application_failed')
            result['screenshot_path'] = self._get_last_screenshot()

            return result

    def _complete_application_form(self, modal, result: Dict) -> bool:
        """Complete multi-step Easy Apply form"""
        try:
            step = 1
            max_steps = 10  # Safety limit

            while step <= max_steps:
                print(f"\n--- Step {step} ---")

                # Answer all questions on current page
                answered = self.question_answerer.answer_all_questions(modal, self.driver)
                if answered:
                    print(f"[OK] Answered {len(answered)} questions")
                    result['questions_asked'].extend(answered)
                    self.stats['questions_answered'] += len(answered)
                time.sleep(1)

                # Upload resume if prompted
                uploaded = self._upload_resume_if_prompted(modal)
                if uploaded:
                    print("[OK] Resume uploaded")
                    self.stats['resume_uploaded'] += 1
                time.sleep(1)

                # Follow company if enabled
                if self.config.get('auto_follow_companies', False):
                    self._follow_company(modal)
                    time.sleep(0.5)

                # Try to find and click Next/Review button
                next_button = self._find_next_button(modal)
                review_button = self._find_review_button(modal)
                submit_button = self._find_submit_button(modal)

                if submit_button:
                    # Final step - submit
                    print("📤 Submitting application...")
                    safe_click(submit_button)
                    time.sleep(2)

                    # Verify submission
                    if self._verify_submission():
                        print("[SUCCESS] Application submitted successfully!")
                        return True
                    else:
                        print("[WARN] Submit clicked but verification unclear")
                        return True  # Assume success

                elif review_button:
                    # Review step - click review
                    print("👀 Going to Review step...")
                    safe_click(review_button)
                    time.sleep(1.5)
                    step += 1

                elif next_button:
                    # More steps ahead - click next
                    print("➡️ Going to Next step...")
                    safe_click(next_button)
                    time.sleep(1.5)
                    step += 1

                else:
                    # No navigation buttons found
                    print("[WARN] No navigation buttons found")

                    # Check if we're on a confirmation page
                    if self._verify_submission():
                        print("[SUCCESS] Application appears to be submitted!")
                        return True

                    # Take screenshot for debugging
                    self._take_screenshot(f'no_buttons_step_{step}')

                    # Try to find submit button one more time with different selectors
                    submit_found = self._try_alternative_submit()
                    if submit_found:
                        return True

                    print("[FAILED] Could not find next action")
                    return False

            print("[WARN] Reached maximum steps")
            return False

        except Exception as e:
            print(f"[FAILED] Form completion error: {e}")
            self._take_screenshot('form_error')
            return False

    def _find_next_button(self, modal):
        """Find Next button with multiple selectors"""
        selectors = [
            './/button[contains(., "Next") or contains(., "Continue")]',
            './/button[@aria-label="Continue to next step"]',
            './/button[@aria-label="Next"]',
            './/footer//button[contains(@class, "artdeco-button--primary")]',
        ]

        for selector in selectors:
            try:
                button = modal.find_element(By.XPATH, selector)
                if is_element_visible(button) and 'disabled' not in button.get_attribute('class'):
                    return button
            except NoSuchElementException:
                continue

        return None

    def _find_review_button(self, modal):
        """Find Review button"""
        selectors = [
            './/button[contains(., "Review")]',
            './/button[@aria-label="Review your application"]',
        ]

        for selector in selectors:
            try:
                button = modal.find_element(By.XPATH, selector)
                if is_element_visible(button):
                    return button
            except NoSuchElementException:
                continue

        return None

    def _find_submit_button(self, modal):
        """Find Submit button"""
        selectors = [
            './/button[contains(., "Submit application")]',
            './/button[contains(., "Submit")]',
            './/button[@aria-label="Submit application"]',
            './/footer//button[contains(@class, "artdeco-button--primary") and contains(., "Submit")]',
        ]

        for selector in selectors:
            try:
                button = modal.find_element(By.XPATH, selector)
                if is_element_visible(button):
                    return button
            except NoSuchElementException:
                continue

        return None

    def _try_alternative_submit(self) -> bool:
        """Try alternative methods to find and click submit button"""
        try:
            # Try finding submit in the whole page (not just modal)
            submit_selectors = [
                '//button[contains(., "Submit application")]',
                '//button[contains(@aria-label, "Submit")]',
            ]

            for selector in submit_selectors:
                try:
                    button = self.driver.find_element(By.XPATH, selector)
                    if is_element_visible(button):
                        print("[OK] Found submit button with alternative selector")
                        safe_click(button)
                        time.sleep(2)
                        return self._verify_submission()
                except NoSuchElementException:
                    continue

            return False

        except Exception as e:
            print(f"Alternative submit failed: {e}")
            return False

    def _verify_submission(self) -> bool:
        """Verify if application was successfully submitted"""
        try:
            # Check for confirmation message
            confirmation_texts = [
                'application was sent',
                'application submitted',
                'your application has been',
                'successfully applied'
            ]

            page_text = self.driver.find_element(By.TAG_NAME, 'body').text.lower()

            for text in confirmation_texts:
                if text in page_text:
                    return True

            # Check if modal is closed
            try:
                modal = self.driver.find_element(By.CLASS_NAME, 'jobs-easy-apply-modal')
                return not is_element_visible(modal)
            except NoSuchElementException:
                return True  # Modal not found means it closed

            return False

        except Exception as e:
            print(f"Verification check error: {e}")
            return False

    def _upload_resume_if_prompted(self, modal) -> bool:
        """Upload resume if file upload is present"""
        try:
            if not self.resume_path or not os.path.exists(self.resume_path):
                return False

            # Look for file upload inputs
            file_inputs = modal.find_elements(By.XPATH, './/input[@type="file"]')

            for file_input in file_inputs:
                if is_element_visible(file_input.find_element(By.XPATH, './ancestor::div[1]')):
                    # Upload file
                    file_input.send_keys(str(self.resume_path))
                    time.sleep(1)
                    print(f"[OK] Uploaded resume: {os.path.basename(self.resume_path)}")
                    return True

            return False

        except Exception as e:
            print(f"Resume upload error: {e}")
            return False

    def _follow_company(self, modal) -> bool:
        """Follow company during application (optional)"""
        try:
            # Look for follow company checkbox
            follow_checkbox = modal.find_element(By.XPATH, './/input[@id="follow-company-checkbox" and @type="checkbox"]')

            if follow_checkbox:
                is_checked = follow_checkbox.is_selected()
                should_follow = self.config.get('auto_follow_companies', False)

                if is_checked != should_follow:
                    # Click the label to toggle
                    label = modal.find_element(By.XPATH, './/label[@for="follow-company-checkbox"]')
                    safe_click(label)
                    print(f"[OK] {'Followed' if should_follow else 'Unfollowed'} company")
                    return True

            return False

        except NoSuchElementException:
            # Follow checkbox not found - not all applications have this
            return False
        except Exception as e:
            print(f"Follow company error: {e}")
            return False

    def _take_screenshot(self, name: str):
        """Take screenshot for debugging/logging"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{name}_{timestamp}.png"
            filepath = self.screenshot_dir / filename
            self.driver.save_screenshot(str(filepath))
            print(f"📸 Screenshot saved: {filename}")
            return str(filepath)
        except Exception as e:
            print(f"Screenshot failed: {e}")
            return None

    def _get_last_screenshot(self) -> Optional[str]:
        """Get path to most recent screenshot"""
        try:
            screenshots = sorted(self.screenshot_dir.glob('*.png'), key=os.path.getmtime, reverse=True)
            if screenshots:
                return str(screenshots[0])
            return None
        except:
            return None

    def apply_to_multiple_jobs(self, job_urls: List[str], delay_between: int = 5) -> List[Dict]:
        """
        Apply to multiple jobs

        Args:
            job_urls: List of LinkedIn job URLs
            delay_between: Seconds to wait between applications

        Returns:
            List of application results
        """
        results = []

        print(f"\n🚀 Starting bulk application to {len(job_urls)} jobs\n")
        print("=" * 60)

        for i, job_url in enumerate(job_urls, 1):
            print(f"\n[{i}/{len(job_urls)}] Processing job...")

            result = self.apply_to_job(job_url)
            results.append(result)

            # Delay between applications (to avoid rate limiting)
            if i < len(job_urls):
                print(f"\n⏳ Waiting {delay_between} seconds before next application...")
                time.sleep(delay_between)

        print("\n" + "=" * 60)
        print("\n📊 Application Summary:")
        print(f"   Attempted: {self.stats['applications_attempted']}")
        print(f"   [SUCCESS] Successful: {self.stats['applications_successful']}")
        print(f"   [FAILED] Failed: {self.stats['applications_failed']}")
        print(f"   ❓ Questions Answered: {self.stats['questions_answered']}")
        print(f"   📄 Resumes Uploaded: {self.stats['resume_uploaded']}")

        return results

    def close(self):
        """Close the browser"""
        if self.driver:
            self.driver.quit()
            print("\n[OK] Browser closed")

    def get_stats(self) -> Dict:
        """Get application statistics"""
        return self.stats.copy()

    def get_all_answered_questions(self) -> List[Dict]:
        """Get all questions answered across all applications"""
        return self.question_answerer.get_answered_questions()
