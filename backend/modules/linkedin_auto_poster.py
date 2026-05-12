"""
LinkedIn Auto-Poster - Automatically post content to LinkedIn
"""

import os
import time
from pathlib import Path
from typing import Optional, Dict
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import undetected_chromedriver as uc
from dotenv import load_dotenv

# Load environment variables
project_root = Path(__file__).parent.parent.parent
env_path = project_root / '.env'
if env_path.exists():
    load_dotenv(dotenv_path=env_path)


class LinkedInAutoPoster:
    """Automatically post content to LinkedIn"""

    def __init__(self):
        self.driver = None
        self.linkedin_email = os.getenv('LINKEDIN_EMAIL')
        self.linkedin_password = os.getenv('LINKEDIN_PASSWORD')

        if not self.linkedin_email or not self.linkedin_password:
            raise ValueError("LINKEDIN_EMAIL and LINKEDIN_PASSWORD must be set in .env")

    def initialize_driver(self):
        """Initialize undetected Chrome driver"""
        if self.driver:
            return

        print("Initializing Chrome driver...")
        options = uc.ChromeOptions()
        options.add_argument('--start-maximized')
        options.add_argument('--disable-blink-features=AutomationControlled')

        self.driver = uc.Chrome(options=options, version_main=146)
        print("Chrome driver initialized")

    def login_to_linkedin(self) -> bool:
        """Log into LinkedIn"""
        try:
            print("Logging into LinkedIn...")
            self.driver.get('https://www.linkedin.com/login')
            time.sleep(3)

            # Enter email
            email_field = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, 'username'))
            )
            email_field.send_keys(self.linkedin_email)

            # Enter password
            password_field = self.driver.find_element(By.ID, 'password')
            password_field.send_keys(self.linkedin_password)

            # Click sign in
            sign_in_button = self.driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
            sign_in_button.click()

            time.sleep(5)

            # Check if login successful (should be on feed)
            if 'feed' in self.driver.current_url or 'mynetwork' in self.driver.current_url:
                print("Successfully logged into LinkedIn")
                return True
            else:
                print("Login may have failed or requires verification")
                return False

        except Exception as e:
            print(f"Error logging into LinkedIn: {e}")
            return False

    def create_post(self, content: str, wait_after: int = 3) -> Dict:
        """
        Create and publish a LinkedIn post

        Args:
            content: The post content to publish
            wait_after: Seconds to wait after posting (default 3)

        Returns:
            Dict with success status and message
        """
        try:
            # Navigate to feed if not already there
            if 'feed' not in self.driver.current_url:
                self.driver.get('https://www.linkedin.com/feed/')
                time.sleep(3)

            print(f"Creating post: {content[:50]}...")

            # Click "Start a post" button - try multiple selectors
            start_post_selectors = [
                'button.artdeco-button--muted.share-box-feed-entry__trigger',
                'button[aria-label*="Start a post"]',
                '.share-box-feed-entry__trigger',
                'button.share-box-feed-entry__trigger',
                '[data-control-name="share_box_trigger"]',
                'button:has-text("Start a post")',
                '.share-box__open'
            ]

            start_button = None
            for selector in start_post_selectors:
                try:
                    start_button = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                    )
                    if start_button:
                        break
                except:
                    continue

            if not start_button:
                # Fallback: try finding any visible clickable element with "Start a post" text
                try:
                    clickable_elements = self.driver.find_elements(By.XPATH, "//*[contains(text(), 'Start a post')]")
                    for elem in clickable_elements:
                        if elem.is_displayed():
                            start_button = elem
                            break
                except:
                    pass

            if not start_button:
                return {
                    'success': False,
                    'message': 'Could not find "Start a post" button. Please ensure you are logged into LinkedIn.'
                }

            start_button.click()
            time.sleep(2)

            # Find the post editor - try multiple selectors for 2024/2025 LinkedIn
            editor_selectors = [
                'div.ql-editor[contenteditable="true"]',
                'div[data-placeholder][contenteditable="true"]',
                'div.share-creation-state__text-editor div[contenteditable="true"]',
                'div[role="textbox"][contenteditable="true"]',
                '.ql-editor p',
                'div.ql-editor.ql-blank',
                '[aria-label*="Text editor"]'
            ]

            editor = None
            for selector in editor_selectors:
                try:
                    editor = WebDriverWait(self.driver, 5).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                    if editor:
                        break
                except:
                    continue

            if not editor:
                return {
                    'success': False,
                    'message': 'Could not find post editor. LinkedIn UI may have changed.'
                }

            # Type the content
            editor.click()
            time.sleep(1)
            editor.send_keys(content)
            time.sleep(2)

            # Find and click the "Post" button - try multiple selectors
            post_button_selectors = [
                'button.share-actions__primary-action',
                'button[aria-label*="Post"]',
                'button.share-actions__primary-action[type="button"]',
                'button[data-control-name="share.post"]',
                '.share-box__submit button',
                'button:has-text("Post")',
                'button.artdeco-button--primary:has-text("Post")'
            ]

            post_button = None
            for selector in post_button_selectors:
                try:
                    post_button = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                    )
                    if post_button and post_button.is_displayed():
                        break
                except:
                    continue

            if not post_button:
                # Fallback: try XPath
                try:
                    post_button = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Post')]")
                except:
                    pass

            if not post_button:
                return {
                    'success': False,
                    'message': 'Could not find Post button. Content was entered but not published.'
                }

            # Click Post button
            post_button.click()
            time.sleep(wait_after)

            print(f"Post published successfully!")

            return {
                'success': True,
                'message': 'Post published successfully to LinkedIn'
            }

        except Exception as e:
            print(f"Error creating post: {e}")

            # Take screenshot for debugging
            try:
                screenshot_path = f"debug_posting_{int(time.time())}.png"
                self.driver.save_screenshot(screenshot_path)
                print(f"Debug screenshot saved: {screenshot_path}")
            except:
                pass

            return {
                'success': False,
                'message': f'Error posting to LinkedIn: {str(e)}'
            }

    def post_multiple(self, posts: list, delay_between: int = 10) -> Dict:
        """
        Post multiple pieces of content with delays

        Args:
            posts: List of post content strings
            delay_between: Seconds to wait between posts (default 10)

        Returns:
            Dict with success count and results
        """
        results = []
        successful = 0

        for i, content in enumerate(posts):
            print(f"\nPosting {i+1}/{len(posts)}...")

            result = self.create_post(content)
            results.append(result)

            if result['success']:
                successful += 1

            # Wait between posts (except after last one)
            if i < len(posts) - 1:
                print(f"Waiting {delay_between} seconds before next post...")
                time.sleep(delay_between)

        return {
            'total': len(posts),
            'successful': successful,
            'failed': len(posts) - successful,
            'results': results
        }

    def close(self):
        """Close the browser"""
        if self.driver:
            self.driver.quit()
            self.driver = None
            print("Browser closed")


# Test function
if __name__ == "__main__":
    poster = LinkedInAutoPoster()

    try:
        poster.initialize_driver()

        if poster.login_to_linkedin():
            # Test with a single post
            test_content = """Just shipped a new feature!

Building in public has taught me more than any course ever could.

The feedback loop is instant. The accountability is real. And the community support? Unmatched.

What's something you learned by doing rather than studying?"""

            result = poster.create_post(test_content)
            print(f"\nResult: {result}")

    finally:
        input("Press Enter to close browser...")
        poster.close()
