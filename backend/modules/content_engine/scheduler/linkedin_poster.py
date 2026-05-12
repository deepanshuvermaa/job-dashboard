"""Post content to LinkedIn"""
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from backend.core.browser.stealth_browser import StealthBrowser, HumanBehavior
from backend.core.browser.session_manager import SessionManager
import time

class LinkedInPoster:
    """Post to LinkedIn with stealth"""

    def __init__(self, user_id: str):
        self.user_id = user_id
        self.session_manager = SessionManager(user_id)
        self.driver = None

    async def post(self, content: str, image_path: str = None) -> dict:
        """
        Post to LinkedIn

        Returns:
            {
                'success': bool,
                'post_id': str,
                'url': str,
                'error': str
            }
        """
        try:
            # Create browser
            self.driver = StealthBrowser.create(headless=False, use_profile=True)

            # Load session
            if not self.session_manager.load_cookies(self.driver):
                # Need to log in
                await self._login()

            # Check if still logged in
            if not self.session_manager.is_logged_in(self.driver):
                await self._login()

            # Navigate to feed
            self.driver.get("https://www.linkedin.com/feed/")
            HumanBehavior.random_delay(2, 4)

            # Click "Start a post"
            start_post_btn = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CLASS_NAME, "share-box-feed-entry__trigger"))
            )
            HumanBehavior.smooth_scroll(self.driver, start_post_btn)
            HumanBehavior.random_delay(1, 2)
            start_post_btn.click()

            # Wait for modal
            HumanBehavior.random_delay(1, 2)

            # Find text area
            text_area = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "ql-editor"))
            )

            # Type content (slowly)
            HumanBehavior.slow_type(text_area, content, delay=0.05)

            HumanBehavior.random_delay(2, 3)

            # Upload image if provided
            if image_path:
                await self._upload_image(image_path)

            # Click Post button
            post_button = self.driver.find_element(By.XPATH, "//button[contains(@class, 'share-actions__primary-action')]")
            HumanBehavior.random_delay(1, 2)
            post_button.click()

            # Wait for post to complete
            time.sleep(5)

            # Save session
            self.session_manager.save_cookies(self.driver)

            return {
                'success': True,
                'post_id': 'posted',  # LinkedIn doesn't give us ID easily
                'url': self.driver.current_url,
                'error': None
            }

        except Exception as e:
            return {
                'success': False,
                'post_id': None,
                'url': None,
                'error': str(e)
            }

        finally:
            if self.driver:
                self.driver.quit()

    async def _login(self):
        """Manual login flow"""
        from backend.core.config import settings

        self.driver.get("https://www.linkedin.com/login")
        HumanBehavior.random_delay(2, 3)

        # Email
        email_field = self.driver.find_element(By.ID, "username")
        HumanBehavior.slow_type(email_field, settings.LINKEDIN_EMAIL)

        # Password
        password_field = self.driver.find_element(By.ID, "password")
        HumanBehavior.slow_type(password_field, settings.LINKEDIN_PASSWORD)

        # Submit
        HumanBehavior.random_delay(1, 2)
        submit_btn = self.driver.find_element(By.XPATH, "//button[@type='submit']")
        submit_btn.click()

        # Wait for login (may need 2FA)
        print("⚠️  Check browser for 2FA if required...")
        time.sleep(15)  # Give time for 2FA

        # Save cookies
        self.session_manager.save_cookies(self.driver)

    async def _upload_image(self, image_path: str):
        """Upload image to post"""
        try:
            # Find image upload input
            file_input = self.driver.find_element(By.XPATH, "//input[@type='file']")
            file_input.send_keys(image_path)
            HumanBehavior.random_delay(2, 3)
        except:
            pass  # Image upload failed, continue without
