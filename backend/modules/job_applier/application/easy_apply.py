"""Apply to LinkedIn Easy Apply jobs"""
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from backend.core.browser.stealth_browser import HumanBehavior
from backend.core.ai.llm_router import llm_router
from backend.core.ai.prompts.job_prompts import get_job_answer_prompt
import time

class EasyApplyBot:
    """Handle Easy Apply applications"""

    def __init__(self, driver, user_info: dict):
        self.driver = driver
        self.user_info = user_info
        self.llm = llm_router

    async def apply(self, job_url: str, resume_path: str = None) -> dict:
        """
        Apply to job via Easy Apply

        Returns:
            {
                'success': bool,
                'error': str,
                'answers': dict
            }
        """
        try:
            self.driver.get(job_url)
            HumanBehavior.random_delay(2, 4)

            # Click Easy Apply button
            easy_apply_btn = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CLASS_NAME, "jobs-apply-button"))
            )
            easy_apply_btn.click()
            HumanBehavior.random_delay(1, 2)

            answers = {}

            # Go through form steps
            while True:
                # Check if we're done
                if self._check_review_page():
                    break

                # Answer questions on current page
                page_answers = await self._answer_page_questions()
                answers.update(page_answers)

                # Upload resume if needed
                if resume_path:
                    self._upload_resume(resume_path)

                # Click Next
                if not self._click_next():
                    break

                HumanBehavior.random_delay(2, 3)

            # Submit application
            submit_btn = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Submit')]")
            submit_btn.click()

            HumanBehavior.random_delay(3, 5)

            return {
                'success': True,
                'error': None,
                'answers': answers
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'answers': {}
            }

    async def _answer_page_questions(self) -> dict:
        """Answer questions on current page"""
        answers = {}

        # Find all input fields
        text_inputs = self.driver.find_elements(By.TAG_NAME, "input")
        textareas = self.driver.find_elements(By.TAG_NAME, "textarea")

        for field in text_inputs + textareas:
            try:
                # Get question label
                field_id = field.get_attribute("id")
                label = self.driver.find_element(By.XPATH, f"//label[@for='{field_id}']")
                question = label.text.strip()

                if not question or field.get_attribute("value"):
                    continue

                # Determine field type
                field_type = self._detect_field_type(field, question)

                # Generate answer
                answer = await self._generate_answer(question, field_type)

                # Fill field
                HumanBehavior.slow_type(field, answer, delay=0.05)

                answers[question] = answer

            except:
                continue

        return answers

    def _detect_field_type(self, field, question: str) -> str:
        """Detect what type of answer is needed"""
        question_lower = question.lower()

        if any(word in question_lower for word in ['year', 'experience', 'how many']):
            return 'numeric'
        elif any(word in question_lower for word in ['phone', 'email', 'name']):
            return 'personal_info'
        elif any(word in question_lower for word in ['yes', 'no', 'authorized', 'require']):
            return 'yes_no'
        else:
            return 'text'

    async def _generate_answer(self, question: str, field_type: str) -> str:
        """Generate answer using AI or predefined"""
        # Check for predefined answers
        predefined = {
            'phone': self.user_info.get('phone', ''),
            'email': self.user_info.get('email', ''),
            'name': self.user_info.get('name', ''),
            'linkedin': self.user_info.get('linkedin_url', ''),
        }

        question_lower = question.lower()
        for key, value in predefined.items():
            if key in question_lower and value:
                return value

        # Use AI for other questions
        try:
            prompt = get_job_answer_prompt(question, field_type, self.user_info)
            result = await self.llm.generate(prompt, purpose="job_answer", max_tokens=100)
            return result['text'].strip()
        except:
            return "Yes" if field_type == "yes_no" else "N/A"

    def _upload_resume(self, resume_path: str):
        """Upload resume file"""
        try:
            file_inputs = self.driver.find_elements(By.XPATH, "//input[@type='file']")
            if file_inputs:
                file_inputs[0].send_keys(resume_path)
                HumanBehavior.random_delay(2, 3)
        except:
            pass

    def _check_review_page(self) -> bool:
        """Check if we're on the review page"""
        try:
            submit_btn = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Submit')]")
            return True
        except:
            return False

    def _click_next(self) -> bool:
        """Click Next button"""
        try:
            next_btn = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Next')]")
            next_btn.click()
            return True
        except:
            return False
