"""Stealth browser setup to avoid LinkedIn detection"""
import undetected_chromedriver as uc
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import random
import os

class StealthBrowser:
    """Create anti-detection browser instance"""

    @staticmethod
    def create(headless=False, use_profile=True):
        """Create stealth Chrome browser"""
        options = uc.ChromeOptions()

        # Basic stealth settings
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-gpu')

        # Window size (not headless - LinkedIn detects)
        if headless:
            options.add_argument('--headless=new')

        options.add_argument('--window-size=1920,1080')

        # User agent rotation
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        ]
        options.add_argument(f'user-agent={random.choice(user_agents)}')

        # Disable automation flags
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)

        # Use real Chrome profile (optional but recommended)
        if use_profile:
            profile_path = os.path.join(os.getcwd(), 'sessions', 'chrome_profile')
            os.makedirs(profile_path, exist_ok=True)
            options.add_argument(f'--user-data-dir={profile_path}')

        # Create undetected Chrome instance
        driver = uc.Chrome(options=options, version_main=146)

        # Additional stealth injections
        driver.execute_cdp_cmd('Network.setUserAgentOverride', {
            "userAgent": options.arguments[4].split('=')[1]  # Get the user-agent we set
        })

        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

        return driver

class HumanBehavior:
    """Simulate human-like behavior"""

    @staticmethod
    def random_delay(min_sec=1, max_sec=3):
        """Random delay between actions"""
        import time
        import random
        time.sleep(random.uniform(min_sec, max_sec))

    @staticmethod
    def slow_type(element, text, delay=0.1):
        """Type slowly like a human"""
        import time
        import random
        for char in text:
            element.send_keys(char)
            time.sleep(random.uniform(delay * 0.5, delay * 1.5))

    @staticmethod
    def smooth_scroll(driver, element=None):
        """Scroll smoothly to element or bottom"""
        import time
        if element:
            driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", element)
        else:
            # Scroll in chunks
            total_height = driver.execute_script("return document.body.scrollHeight")
            viewport_height = driver.execute_script("return window.innerHeight")
            current_position = 0

            while current_position < total_height:
                scroll_amount = viewport_height * random.uniform(0.6, 0.9)
                driver.execute_script(f"window.scrollBy(0, {scroll_amount})")
                current_position += scroll_amount
                time.sleep(random.uniform(0.5, 1.5))
