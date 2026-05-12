"""
LinkedIn Auto-Poster using Selenium
"""

import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
try:
    from undetected_chromedriver import Chrome, ChromeOptions
except ImportError:
    Chrome = None
    ChromeOptions = None
import os

class LinkedInPoster:
    def __init__(self, email: str = None, password: str = None, headless: bool = False):
        self.email = email or os.getenv('LINKEDIN_EMAIL')
        self.password = password or os.getenv('LINKEDIN_PASSWORD')
        self.headless = headless
        self.driver = None
        self.logged_in = False

    def _init_driver(self):
        """Initialize undetected Chrome driver"""
        options = ChromeOptions()
        if self.headless:
            options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')

        self.driver = Chrome(options=options, version_main=146)
        self.driver.maximize_window()

    def login(self) -> bool:
        """Login to LinkedIn"""
        try:
            if not self.driver:
                self._init_driver()

            print("Logging into LinkedIn...")
            self.driver.get('https://www.linkedin.com/login')
            time.sleep(2)

            # Enter credentials
            email_field = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, 'username'))
            )
            email_field.send_keys(self.email)

            password_field = self.driver.find_element(By.ID, 'password')
            password_field.send_keys(self.password)

            # Submit
            login_button = self.driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
            login_button.click()

            # Wait for dashboard
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, 'global-nav'))
            )

            print("Successfully logged in!")
            self.logged_in = True
            return True

        except Exception as e:
            print(f"Login failed: {e}")
            return False

    def create_post(self, content: str, hashtags: List[str] = None) -> Dict:
        """Create and publish a LinkedIn post"""
        try:
            if not self.logged_in:
                if not self.login():
                    return {'success': False, 'error': 'Login failed'}

            # Navigate to feed
            self.driver.get('https://www.linkedin.com/feed/')
            time.sleep(2)

            # Click "Start a post" button
            start_post_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[aria-label*="Start a post"]'))
            )
            start_post_button.click()
            time.sleep(1)

            # Find the post text area
            text_area = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '.ql-editor'))
            )

            # Add hashtags to content
            full_content = content
            if hashtags:
                hashtag_str = " ".join([f"#{tag}" for tag in hashtags])
                full_content = f"{content}\n\n{hashtag_str}"

            # Type content
            text_area.click()
            text_area.send_keys(full_content)
            time.sleep(2)

            # Click Post button
            post_button = self.driver.find_element(By.CSS_SELECTOR, 'button[aria-label="Post"]')
            post_button.click()
            time.sleep(3)

            # Get the post URL (approximate - LinkedIn doesn't make this easy)
            post_url = self.driver.current_url

            print("Successfully published post!")
            return {
                'success': True,
                'post_url': post_url,
                'message': 'Post published successfully'
            }

        except Exception as e:
            print(f"Error creating post: {e}")
            return {'success': False, 'error': str(e)}

    def close(self):
        """Close the browser"""
        if self.driver:
            self.driver.quit()
