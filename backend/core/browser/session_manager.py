"""Manage browser sessions and cookies"""
import json
import os
from datetime import datetime, timedelta
from pathlib import Path

class SessionManager:
    """Manage LinkedIn sessions"""

    def __init__(self, user_id):
        self.user_id = user_id
        self.session_dir = Path("sessions") / str(user_id)
        self.session_dir.mkdir(parents=True, exist_ok=True)
        self.cookies_file = self.session_dir / "cookies.json"

    def save_cookies(self, driver):
        """Save browser cookies"""
        cookies = driver.get_cookies()
        with open(self.cookies_file, 'w') as f:
            json.dump(cookies, f)

    def load_cookies(self, driver):
        """Load saved cookies"""
        if not self.cookies_file.exists():
            return False

        try:
            with open(self.cookies_file, 'r') as f:
                cookies = json.load(f)

            driver.get("https://www.linkedin.com")
            for cookie in cookies:
                # Remove domain if it starts with dot
                if 'domain' in cookie and cookie['domain'].startswith('.'):
                    cookie['domain'] = cookie['domain'][1:]
                try:
                    driver.add_cookie(cookie)
                except:
                    pass

            driver.refresh()
            return True
        except:
            return False

    def is_logged_in(self, driver):
        """Check if still logged in"""
        try:
            driver.get("https://www.linkedin.com/feed/")
            # Check if we're on the feed (not login page)
            return "/feed/" in driver.current_url
        except:
            return False

    def clear_session(self):
        """Clear saved session"""
        if self.cookies_file.exists():
            self.cookies_file.unlink()
