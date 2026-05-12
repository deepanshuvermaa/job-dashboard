"""LinkedIn Auto-Messenger - Send personalized DMs to recruiters via Selenium"""
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from typing import List, Dict
from modules.linkedin_job_scraper import LinkedInJobScraper

class LinkedInAutoMessenger:
    """Send automated personalized messages on LinkedIn"""

    def __init__(self, email: str = None, password: str = None):
        # Reuse the job scraper's driver
        self.scraper = LinkedInJobScraper(email, password, headless=False)
        self.driver = None
        self.logged_in = False

    def login(self) -> bool:
        """Login to LinkedIn"""
        if not self.logged_in:
            self.logged_in = self.scraper.login()
            self.driver = self.scraper.driver
        return self.logged_in

    def send_message(self, profile_url: str, message: str, recruiter_name: str = "there") -> bool:
        """Send a LinkedIn message to a specific profile

        Args:
            profile_url: LinkedIn profile URL or messaging compose URL
            message: Message text to send
            recruiter_name: Name of recipient (for logging)

        Returns:
            True if message sent successfully
        """
        try:
            if not self.logged_in:
                if not self.login():
                    return False

            print(f"Sending message to {recruiter_name}...")

            # Navigate to messaging URL
            if 'messaging/compose' in profile_url:
                # Direct messaging URL
                self.driver.get(profile_url)
            elif '/in/' in profile_url:
                # Profile URL - need to convert to messaging
                profile_id = profile_url.split('/in/')[1].split('/')[0].split('?')[0]
                messaging_url = f"https://www.linkedin.com/messaging/compose/?recipient={profile_id}"
                self.driver.get(messaging_url)
            else:
                print(f"Invalid profile URL: {profile_url}")
                return False

            time.sleep(4)  # Longer wait for page load

            # Updated LinkedIn 2024/2025 message box selectors
            message_box_selectors = [
                'div.msg-form__contenteditable[contenteditable="true"]',
                'div[data-placeholder][contenteditable="true"]',
                '.msg-form__contenteditable p',
                'div.msg-form__msg-content-container div[contenteditable="true"]',
                'div[role="textbox"][contenteditable="true"]',
                '.msg-form__contenteditable',
                '[aria-label*="Write a message"]',
                'div.msg-form__compose-message-input div[contenteditable="true"]'
            ]

            message_box = None
            for selector in message_box_selectors:
                try:
                    message_box = WebDriverWait(self.driver, 8).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                    if message_box and message_box.is_displayed():
                        print(f"✓ Found message box with selector: {selector}")
                        break
                except:
                    continue

            if not message_box:
                print("❌ Could not find message input box. Trying alternative approach...")
                # Try clicking on any visible input area
                try:
                    clickable_areas = self.driver.find_elements(By.CSS_SELECTOR, 'div[contenteditable]')
                    for area in clickable_areas:
                        if area.is_displayed():
                            message_box = area
                            print("Found message box via alternative method")
                            break
                except:
                    pass

            if not message_box:
                print("❌ Failed to find message box after all attempts")
                return False

            # Click on message box to focus
            try:
                message_box.click()
                time.sleep(1)
            except:
                print("Could not click message box, trying to send keys anyway")

            # Type message (try multiple methods)
            try:
                message_box.clear()
                message_box.send_keys(message)
                time.sleep(1.5)
                print(f"✓ Typed message ({len(message)} chars)")
            except Exception as e:
                print(f"Error typing message: {e}")
                # Try JavaScript as fallback
                try:
                    self.driver.execute_script(f"arguments[0].innerText = '{message}';", message_box)
                    print("✓ Inserted message via JavaScript")
                except:
                    print("❌ Failed to insert message")
                    return False

            # Wait a moment for LinkedIn to register the input
            time.sleep(2)

            # Updated Send button selectors for 2024/2025
            send_button_selectors = [
                'button.msg-form__send-button[type="submit"]',
                'button[aria-label*="Send"]',
                'button.msg-form__send-btn',
                'button[data-control-name="send"]',
                'button.artdeco-button--primary[type="submit"]',
                '.msg-form__send-button',
                'button:has-text("Send")',
                'footer button[type="submit"]'
            ]

            send_button = None
            for selector in send_button_selectors:
                try:
                    buttons = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for btn in buttons:
                        if btn.is_displayed() and btn.is_enabled():
                            send_button = btn
                            print(f"✓ Found Send button with selector: {selector}")
                            break
                    if send_button:
                        break
                except:
                    continue

            if not send_button:
                # Try finding by text
                try:
                    all_buttons = self.driver.find_elements(By.TAG_NAME, 'button')
                    for btn in all_buttons:
                        if btn.is_displayed() and 'send' in btn.text.lower():
                            send_button = btn
                            print("✓ Found Send button by text")
                            break
                except:
                    pass

            if send_button and send_button.is_enabled():
                send_button.click()
                time.sleep(2)
                print(f"✅ Message sent to {recruiter_name}")
                return True
            else:
                print(f"❌ Send button not found or not enabled for {recruiter_name}")
                # Take screenshot for debugging
                try:
                    self.driver.save_screenshot(f"debug_messaging_{recruiter_name.replace(' ', '_')}.png")
                    print("Saved screenshot for debugging")
                except:
                    pass
                return False

        except Exception as e:
            print(f"Error sending message to {recruiter_name}: {e}")
            return False

    def send_bulk_messages(
        self,
        messages: List[Dict],
        delay_seconds: int = 30,
        max_messages: int = 10
    ) -> Dict:
        """Send multiple messages with delays

        Args:
            messages: List of {dm_link, message, recruiter_name, job_title}
            delay_seconds: Delay between messages (to avoid rate limiting)
            max_messages: Maximum messages to send

        Returns:
            {sent: int, failed: int, details: []}
        """
        if not self.logged_in:
            if not self.login():
                return {'sent': 0, 'failed': len(messages), 'details': []}

        results = {
            'sent': 0,
            'failed': 0,
            'details': []
        }

        for i, msg_data in enumerate(messages[:max_messages]):
            recruiter_name = msg_data.get('recruiter_name', 'Recruiter')
            job_title = msg_data.get('job_title', 'Position')
            dm_link = msg_data.get('dm_link')
            message = msg_data.get('message')

            if not dm_link or not message:
                print(f"Skipping message {i+1} - missing dm_link or message")
                results['failed'] += 1
                continue

            print(f"\n[{i+1}/{len(messages)}] Messaging {recruiter_name} about {job_title}...")

            success = self.send_message(dm_link, message, recruiter_name)

            result_detail = {
                'recruiter_name': recruiter_name,
                'job_title': job_title,
                'success': success
            }

            if success:
                results['sent'] += 1
            else:
                results['failed'] += 1

            results['details'].append(result_detail)

            # Delay before next message (avoid rate limiting)
            if i < len(messages) - 1:
                print(f"Waiting {delay_seconds} seconds before next message...")
                time.sleep(delay_seconds)

        return results

    def send_connection_request(
        self,
        profile_url: str,
        message: str = None,
        person_name: str = "there"
    ) -> bool:
        """Send a connection request with optional note

        Args:
            profile_url: LinkedIn profile URL
            message: Optional connection note (max 200 chars)
            person_name: Name of person

        Returns:
            True if request sent successfully
        """
        try:
            if not self.logged_in:
                if not self.login():
                    return False

            print(f"Sending connection request to {person_name}...")

            # Navigate to profile
            self.driver.get(profile_url)
            time.sleep(3)

            # Find Connect button
            connect_button_selectors = [
                'button[aria-label*="Connect"]',
                'button:has-text("Connect")',
                '.pvs-profile-actions__action button'
            ]

            connect_button = None
            for selector in connect_button_selectors:
                try:
                    connect_button = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if connect_button:
                        break
                except:
                    continue

            if not connect_button:
                print(f"Connect button not found for {person_name}")
                return False

            connect_button.click()
            time.sleep(2)

            # If message provided, add note
            if message:
                try:
                    # Click "Add a note" button
                    add_note_button = self.driver.find_element(By.CSS_SELECTOR, 'button[aria-label*="note"]')
                    add_note_button.click()
                    time.sleep(1)

                    # Find note textarea
                    note_textarea = self.driver.find_element(By.CSS_SELECTOR, 'textarea[name="message"]')
                    note_textarea.send_keys(message[:200])  # LinkedIn limit
                    time.sleep(1)
                except:
                    print("Could not add note to connection request")

            # Click Send button
            send_button = self.driver.find_element(By.CSS_SELECTOR, 'button[aria-label*="Send"]')
            send_button.click()
            time.sleep(2)

            print(f"✓ Connection request sent to {person_name}")
            return True

        except Exception as e:
            print(f"Error sending connection request to {person_name}: {e}")
            return False

    def close(self):
        """Close browser"""
        if self.scraper:
            self.scraper.close()


# Test
if __name__ == "__main__":
    messenger = LinkedInAutoMessenger()

    test_message = """Hi Sarah,

I came across the Senior React Developer position at Google and was immediately drawn to it. With my 5+ years of experience in React, TypeScript, and modern web technologies, I believe I could bring significant value to your frontend team.

I'd love to discuss how my background aligns with what you're looking for. Would you be open to a brief conversation?

Thanks for considering!
Deepanshu"""

    # This would be a real LinkedIn messaging URL
    test_dm_link = "https://www.linkedin.com/messaging/compose/?recipient=sarahjohnson"

    print("Test auto-messenger (will not actually send unless you uncomment):")
    print(f"Would send to: {test_dm_link}")
    print(f"Message: {test_message}")

    # Uncomment to test:
    # messenger.send_message(test_dm_link, test_message, "Sarah Johnson")
