"""
Element Detection and Interaction Utilities for LinkedIn Automation
Based on GodsScion's approach with enhancements
"""

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from typing import Optional, List
import time
import re


def find_by_class(driver, class_name: str, timeout: int = 5):
    """Find element by class name with wait"""
    try:
        element = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.CLASS_NAME, class_name))
        )
        return element
    except TimeoutException:
        return None


def find_by_xpath(driver, xpath: str, timeout: int = 5):
    """Find element by XPath with wait"""
    try:
        element = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.XPATH, xpath))
        )
        return element
    except TimeoutException:
        return None


def find_all_by_xpath(driver, xpath: str, timeout: int = 5):
    """Find all elements by XPath with wait"""
    try:
        WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.XPATH, xpath))
        )
        return driver.find_elements(By.XPATH, xpath)
    except TimeoutException:
        return []


def wait_span_click(parent_element, span_text: str, wait_time: int = 2):
    """Click button containing specific span text"""
    try:
        xpath = f'.//button[contains(., "{span_text}")]'
        button = parent_element.find_element(By.XPATH, xpath)
        time.sleep(wait_time)
        button.click()
        return True
    except NoSuchElementException:
        return False


def safe_click(element, wait_before: float = 0.5):
    """Safely click an element with scroll into view"""
    try:
        time.sleep(wait_before)
        # Scroll element into view
        element.location_once_scrolled_into_view
        time.sleep(0.3)
        element.click()
        return True
    except Exception as e:
        print(f"Click failed: {e}")
        return False


def safe_send_keys(element, text: str, clear_first: bool = True):
    """Safely send keys to an input element"""
    try:
        if clear_first:
            element.clear()
        element.send_keys(text)
        return True
    except Exception as e:
        print(f"Send keys failed: {e}")
        return False


def is_element_visible(element) -> bool:
    """Check if element is visible and displayed"""
    try:
        return element.is_displayed() and element.is_enabled()
    except:
        return False


def find_button_by_text(parent_element, button_text: str, partial: bool = True):
    """Find button by text content"""
    try:
        if partial:
            xpath = f'.//button[contains(., "{button_text}")]'
        else:
            xpath = f'.//button[normalize-space(.)="{button_text}"]'
        return parent_element.find_element(By.XPATH, xpath)
    except NoSuchElementException:
        return None


def find_input_by_label(parent_element, label_text: str, partial: bool = True):
    """Find input element by associated label text"""
    try:
        if partial:
            xpath = f'.//label[contains(., "{label_text}")]'
        else:
            xpath = f'.//label[normalize-space(.)="{label_text}"]'

        label = parent_element.find_element(By.XPATH, xpath)
        input_id = label.get_attribute('for')

        if input_id:
            return parent_element.find_element(By.ID, input_id)
        else:
            # Try to find input as sibling or child
            try:
                return label.find_element(By.XPATH, './/following-sibling::input | .//input')
            except:
                return None
    except NoSuchElementException:
        return None


def get_all_form_fields(modal_element):
    """Extract all form fields from a modal"""
    fields = {
        'text_inputs': [],
        'textareas': [],
        'selects': [],
        'radio_groups': [],
        'checkboxes': []
    }

    # Text inputs
    try:
        inputs = modal_element.find_elements(By.XPATH, './/input[@type="text" or @type="email" or @type="tel" or @type="number" or not(@type)]')
        for inp in inputs:
            if is_element_visible(inp):
                fields['text_inputs'].append(inp)
    except:
        pass

    # Textareas
    try:
        textareas = modal_element.find_elements(By.TAG_NAME, 'textarea')
        for ta in textareas:
            if is_element_visible(ta):
                fields['textareas'].append(ta)
    except:
        pass

    # Select dropdowns
    try:
        selects = modal_element.find_elements(By.TAG_NAME, 'select')
        for sel in selects:
            if is_element_visible(sel):
                fields['selects'].append(sel)
    except:
        pass

    # Radio buttons
    try:
        radios = modal_element.find_elements(By.XPATH, './/input[@type="radio"]')
        for radio in radios:
            if is_element_visible(radio):
                fields['radio_groups'].append(radio)
    except:
        pass

    # Checkboxes
    try:
        checkboxes = modal_element.find_elements(By.XPATH, './/input[@type="checkbox"]')
        for cb in checkboxes:
            if is_element_visible(cb):
                fields['checkboxes'].append(cb)
    except:
        pass

    return fields


def get_question_label(input_element):
    """Get the question/label text for an input element"""
    try:
        # Try to find associated label
        input_id = input_element.get_attribute('id')
        if input_id:
            try:
                label = input_element.find_element(By.XPATH, f'//label[@for="{input_id}"]')
                return label.text.strip()
            except:
                pass

        # Try parent label
        try:
            parent = input_element.find_element(By.XPATH, './ancestor::label[1]')
            return parent.text.strip()
        except:
            pass

        # Try aria-label
        aria_label = input_element.get_attribute('aria-label')
        if aria_label:
            return aria_label.strip()

        # Try placeholder
        placeholder = input_element.get_attribute('placeholder')
        if placeholder:
            return placeholder.strip()

        # Try previous sibling or parent text
        try:
            parent_div = input_element.find_element(By.XPATH, './ancestor::div[contains(@class, "form") or contains(@class, "field")][1]')
            text = parent_div.text.strip()
            if text:
                return text.split('\n')[0]  # First line usually has the question
        except:
            pass

        return "Unknown Question"
    except Exception as e:
        return f"Error extracting label: {e}"


def scroll_to_element(driver, element):
    """Scroll element into view smoothly"""
    try:
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", element)
        time.sleep(0.5)
        return True
    except:
        return False


def wait_for_element_clickable(driver, by, value, timeout: int = 10):
    """Wait for element to be clickable"""
    try:
        element = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable((by, value))
        )
        return element
    except TimeoutException:
        return None


def is_easy_apply_available(driver) -> bool:
    """Check if Easy Apply button is available for current job"""
    try:
        easy_apply_button = driver.find_element(By.XPATH, '//button[contains(@class, "jobs-apply-button") and contains(., "Easy Apply")]')
        return is_element_visible(easy_apply_button)
    except NoSuchElementException:
        return False


def get_easy_apply_button(driver):
    """Get Easy Apply button element"""
    try:
        # Multiple selectors for Easy Apply button
        selectors = [
            '//button[contains(@class, "jobs-apply-button") and contains(., "Easy Apply")]',
            '//button[contains(., "Easy Apply")]',
            '//button[@aria-label="Easy Apply"]',
            '//button[contains(@class, "jobs-apply") and not(contains(@class, "disabled"))]'
        ]

        for selector in selectors:
            try:
                button = driver.find_element(By.XPATH, selector)
                if is_element_visible(button):
                    return button
            except NoSuchElementException:
                continue

        return None
    except Exception as e:
        print(f"Error finding Easy Apply button: {e}")
        return None


def get_easy_apply_modal(driver, timeout: int = 5):
    """Get Easy Apply modal element"""
    try:
        modal = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.CLASS_NAME, "jobs-easy-apply-modal"))
        )
        return modal
    except TimeoutException:
        # Try alternative selectors
        try:
            modal = driver.find_element(By.XPATH, '//div[contains(@class, "artdeco-modal") and contains(@aria-label, "Easy Apply")]')
            return modal
        except:
            return None


def extract_text_from_element(element) -> str:
    """Safely extract text from element"""
    try:
        return element.text.strip()
    except:
        try:
            return element.get_attribute('textContent').strip()
        except:
            return ""


def fuzzy_match_option(target: str, options: List[str], threshold: float = 0.6) -> Optional[str]:
    """Fuzzy match target string with list of options"""
    target_lower = target.lower()
    best_match = None
    best_score = 0

    for option in options:
        option_lower = option.lower()

        # Exact match
        if target_lower == option_lower:
            return option

        # Contains match
        if target_lower in option_lower or option_lower in target_lower:
            score = len(target_lower) / len(option_lower)
            if score > best_score:
                best_score = score
                best_match = option

    if best_score >= threshold:
        return best_match

    return None


def extract_number_from_text(text: str) -> Optional[int]:
    """Extract first number from text"""
    try:
        match = re.search(r'\d+', text)
        if match:
            return int(match.group())
        return None
    except:
        return None
