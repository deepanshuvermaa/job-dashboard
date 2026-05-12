"""
Intelligent Question Answering System for LinkedIn Easy Apply
Based on GodsScion's approach with AI enhancements
"""

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
from typing import Dict, List, Optional, Any
import re
import time
from .clickers_and_finders import (
    get_question_label, safe_send_keys, safe_click,
    fuzzy_match_option, extract_number_from_text,
    is_element_visible, scroll_to_element
)


class QuestionAnswerer:
    """Intelligent question answering for LinkedIn Easy Apply forms"""

    def __init__(self, user_config: Dict[str, Any], ai_client=None):
        """
        Initialize with user configuration

        Args:
            user_config: Dictionary with user's personal information and preferences
            ai_client: OpenAI client for AI-powered answers (optional)
        """
        self.config = user_config
        self.ai_client = ai_client
        self.answered_questions = []

        # Common question patterns and their handlers
        self.question_patterns = {
            # Personal Information
            r'(first|given)\s*name': self._answer_first_name,
            r'(last|sur|family)\s*name': self._answer_last_name,
            r'(full\s*)?name': self._answer_full_name,
            r'email': self._answer_email,
            r'phone|mobile|contact\s*number': self._answer_phone,
            r'(current\s*)?(city|location|address)': self._answer_location,
            r'(zip|postal)\s*code': self._answer_zip_code,

            # Professional Information
            r'linkedin\s*(profile|url)': self._answer_linkedin_url,
            r'portfolio|website|personal\s*site': self._answer_portfolio,
            r'github': self._answer_github,

            # Experience & Education
            r'years?\s*of\s*experience': self._answer_years_experience,
            r'current\s*(company|employer)': self._answer_current_company,
            r'current\s*(title|position|role)': self._answer_current_title,
            r'highest\s*(degree|education|qualification)': self._answer_education_level,
            r'(university|college|school)': self._answer_university,
            r'graduation\s*(year|date)': self._answer_graduation_year,

            # Work Authorization & Availability
            r'(authorized|eligible|allowed)\s*to\s*work': self._answer_work_authorization,
            r'(require|need)\s*(visa|sponsorship)': self._answer_visa_sponsorship,
            r'(notice\s*period|availability|start\s*date)': self._answer_notice_period,
            r'willing\s*to\s*relocate': self._answer_willing_to_relocate,
            r'(currently\s*employed|working)': self._answer_currently_employed,

            # Compensation
            r'(current|present)\s*(salary|compensation|ctc)': self._answer_current_salary,
            r'(expected|desired)\s*(salary|compensation|ctc)': self._answer_expected_salary,

            # Yes/No Questions
            r'are\s*you': self._answer_yes_no_question,
            r'do\s*you': self._answer_yes_no_question,
            r'have\s*you': self._answer_yes_no_question,
            r'can\s*you': self._answer_yes_no_question,
            r'will\s*you': self._answer_yes_no_question,

            # Cover Letter & Additional Info
            r'cover\s*letter': self._answer_cover_letter,
            r'(why\s*(you|this|our)|motivation)': self._answer_motivation,
        }

    def answer_all_questions(self, modal_element, driver) -> List[Dict]:
        """Answer all questions in the current Easy Apply form"""
        answered = []

        try:
            # Get all form fields
            from .clickers_and_finders import get_all_form_fields
            fields = get_all_form_fields(modal_element)

            # Answer text inputs
            for input_elem in fields['text_inputs']:
                result = self._answer_text_input(input_elem, driver)
                if result:
                    answered.append(result)

            # Answer textareas
            for textarea_elem in fields['textareas']:
                result = self._answer_textarea(textarea_elem, driver)
                if result:
                    answered.append(result)

            # Answer select dropdowns
            for select_elem in fields['selects']:
                result = self._answer_select(select_elem, driver)
                if result:
                    answered.append(result)

            # Answer radio buttons
            radio_groups = self._group_radio_buttons(fields['radio_groups'])
            for group_name, radios in radio_groups.items():
                result = self._answer_radio_group(radios, driver)
                if result:
                    answered.append(result)

            # Answer checkboxes
            for checkbox_elem in fields['checkboxes']:
                result = self._answer_checkbox(checkbox_elem, driver)
                if result:
                    answered.append(result)

            self.answered_questions.extend(answered)
            return answered

        except Exception as e:
            print(f"Error answering questions: {e}")
            return answered

    def _answer_text_input(self, input_elem, driver) -> Optional[Dict]:
        """Answer a text input field"""
        try:
            if not is_element_visible(input_elem):
                return None

            question = get_question_label(input_elem)
            answer = self._find_answer_for_question(question, input_elem)

            if answer:
                scroll_to_element(driver, input_elem)
                safe_send_keys(input_elem, str(answer))

                return {
                    'question': question,
                    'answer': answer,
                    'type': 'text_input'
                }

            return None
        except Exception as e:
            print(f"Error answering text input: {e}")
            return None

    def _answer_textarea(self, textarea_elem, driver) -> Optional[Dict]:
        """Answer a textarea field"""
        try:
            if not is_element_visible(textarea_elem):
                return None

            question = get_question_label(textarea_elem)
            answer = self._find_answer_for_question(question, textarea_elem)

            if answer:
                scroll_to_element(driver, textarea_elem)
                safe_send_keys(textarea_elem, str(answer))

                return {
                    'question': question,
                    'answer': answer,
                    'type': 'textarea'
                }

            return None
        except Exception as e:
            print(f"Error answering textarea: {e}")
            return None

    def _answer_select(self, select_elem, driver) -> Optional[Dict]:
        """Answer a select dropdown"""
        try:
            if not is_element_visible(select_elem):
                return None

            question = get_question_label(select_elem)
            select = Select(select_elem)
            options = [opt.text for opt in select.options if opt.text.strip()]

            answer = self._find_answer_for_question(question, select_elem)

            if answer:
                # Try fuzzy matching with available options
                matched_option = fuzzy_match_option(str(answer), options)

                if matched_option:
                    scroll_to_element(driver, select_elem)
                    select.select_by_visible_text(matched_option)

                    return {
                        'question': question,
                        'answer': matched_option,
                        'type': 'select',
                        'options': options
                    }

            return None
        except Exception as e:
            print(f"Error answering select: {e}")
            return None

    def _answer_radio_group(self, radio_elements: List, driver) -> Optional[Dict]:
        """Answer a radio button group"""
        try:
            if not radio_elements:
                return None

            # Get question from first radio button
            question = get_question_label(radio_elements[0])

            # Get all options
            options = []
            for radio in radio_elements:
                label = get_question_label(radio)
                options.append(label)

            answer = self._find_answer_for_question(question, radio_elements[0])

            if answer:
                # Find matching radio button
                matched_option = fuzzy_match_option(str(answer), options)

                if matched_option:
                    # Find and click the matching radio
                    for i, radio in enumerate(radio_elements):
                        if options[i] == matched_option:
                            scroll_to_element(driver, radio)
                            safe_click(radio)

                            return {
                                'question': question,
                                'answer': matched_option,
                                'type': 'radio',
                                'options': options
                            }

            return None
        except Exception as e:
            print(f"Error answering radio group: {e}")
            return None

    def _answer_checkbox(self, checkbox_elem, driver) -> Optional[Dict]:
        """Answer a checkbox"""
        try:
            if not is_element_visible(checkbox_elem):
                return None

            question = get_question_label(checkbox_elem)
            answer = self._find_answer_for_question(question, checkbox_elem)

            if answer:
                should_check = self._interpret_boolean_answer(answer)

                # Check if already in desired state
                is_checked = checkbox_elem.is_selected()

                if should_check and not is_checked:
                    scroll_to_element(driver, checkbox_elem)
                    safe_click(checkbox_elem)
                elif not should_check and is_checked:
                    scroll_to_element(driver, checkbox_elem)
                    safe_click(checkbox_elem)

                return {
                    'question': question,
                    'answer': 'Yes' if should_check else 'No',
                    'type': 'checkbox'
                }

            return None
        except Exception as e:
            print(f"Error answering checkbox: {e}")
            return None

    def _find_answer_for_question(self, question: str, element) -> Optional[str]:
        """Find the appropriate answer for a given question"""
        question_lower = question.lower()

        # Try pattern matching first
        for pattern, handler in self.question_patterns.items():
            if re.search(pattern, question_lower):
                answer = handler(question, element)
                if answer:
                    return answer

        # If no pattern matched, try AI if available
        if self.ai_client:
            return self._ai_answer_question(question, element)

        return None

    def _group_radio_buttons(self, radio_elements: List) -> Dict[str, List]:
        """Group radio buttons by their name attribute"""
        groups = {}
        for radio in radio_elements:
            name = radio.get_attribute('name')
            if name:
                if name not in groups:
                    groups[name] = []
                groups[name].append(radio)
        return groups

    def _interpret_boolean_answer(self, answer: Any) -> bool:
        """Interpret various answer formats as boolean"""
        if isinstance(answer, bool):
            return answer

        answer_str = str(answer).lower()
        return answer_str in ['yes', 'true', '1', 'y']

    # Answer handlers for specific question types

    def _answer_first_name(self, question: str, element) -> Optional[str]:
        return self.config.get('first_name')

    def _answer_last_name(self, question: str, element) -> Optional[str]:
        return self.config.get('last_name')

    def _answer_full_name(self, question: str, element) -> Optional[str]:
        first = self.config.get('first_name', '')
        last = self.config.get('last_name', '')
        return f"{first} {last}".strip() if first or last else None

    def _answer_email(self, question: str, element) -> Optional[str]:
        return self.config.get('email')

    def _answer_phone(self, question: str, element) -> Optional[str]:
        return self.config.get('phone')

    def _answer_location(self, question: str, element) -> Optional[str]:
        return self.config.get('location') or self.config.get('city')

    def _answer_zip_code(self, question: str, element) -> Optional[str]:
        return self.config.get('zip_code')

    def _answer_linkedin_url(self, question: str, element) -> Optional[str]:
        return self.config.get('linkedin_url')

    def _answer_portfolio(self, question: str, element) -> Optional[str]:
        return self.config.get('portfolio_url') or self.config.get('website')

    def _answer_github(self, question: str, element) -> Optional[str]:
        return self.config.get('github_url')

    def _answer_years_experience(self, question: str, element) -> Optional[str]:
        # Extract number from config
        exp = self.config.get('years_of_experience')
        if exp:
            return str(exp)

        # Try to extract from total_experience_display
        exp_display = self.config.get('total_experience_display', '')
        number = extract_number_from_text(exp_display)
        if number:
            return str(number)

        return self.config.get('default_years_experience', '2')

    def _answer_current_company(self, question: str, element) -> Optional[str]:
        return self.config.get('current_company')

    def _answer_current_title(self, question: str, element) -> Optional[str]:
        return self.config.get('current_title') or self.config.get('desired_title')

    def _answer_education_level(self, question: str, element) -> Optional[str]:
        return self.config.get('education_level', 'Bachelor\'s Degree')

    def _answer_university(self, question: str, element) -> Optional[str]:
        return self.config.get('university')

    def _answer_graduation_year(self, question: str, element) -> Optional[str]:
        return self.config.get('graduation_year')

    def _answer_work_authorization(self, question: str, element) -> Optional[str]:
        return self.config.get('work_authorization', 'Yes')

    def _answer_visa_sponsorship(self, question: str, element) -> Optional[str]:
        return self.config.get('requires_visa_sponsorship', 'No')

    def _answer_notice_period(self, question: str, element) -> Optional[str]:
        return self.config.get('notice_period', 'Immediate') or self.config.get('availability', '2 weeks')

    def _answer_willing_to_relocate(self, question: str, element) -> Optional[str]:
        return self.config.get('willing_to_relocate', 'Yes')

    def _answer_currently_employed(self, question: str, element) -> Optional[str]:
        return self.config.get('currently_employed', 'Yes')

    def _answer_current_salary(self, question: str, element) -> Optional[str]:
        return self.config.get('current_salary')

    def _answer_expected_salary(self, question: str, element) -> Optional[str]:
        return self.config.get('expected_salary') or self.config.get('desired_salary')

    def _answer_yes_no_question(self, question: str, element) -> Optional[str]:
        """Generic handler for yes/no questions"""
        question_lower = question.lower()

        # Check for specific patterns
        if any(word in question_lower for word in ['relocate', 'move']):
            return self.config.get('willing_to_relocate', 'Yes')

        if any(word in question_lower for word in ['sponsorship', 'visa', 'h1b']):
            return self.config.get('requires_visa_sponsorship', 'No')

        if any(word in question_lower for word in ['authorized', 'eligible', 'legally']):
            return self.config.get('work_authorization', 'Yes')

        if any(word in question_lower for word in ['employed', 'working', 'job']):
            return self.config.get('currently_employed', 'Yes')

        # Default to Yes for other yes/no questions
        return self.config.get('default_yes_no_answer', 'Yes')

    def _answer_cover_letter(self, question: str, element) -> Optional[str]:
        """Generate or retrieve cover letter"""
        # Check if user has a pre-written cover letter
        cover_letter = self.config.get('cover_letter')
        if cover_letter:
            return cover_letter

        # Try to generate with AI
        if self.ai_client:
            return self._ai_generate_cover_letter()

        return None

    def _answer_motivation(self, question: str, element) -> Optional[str]:
        """Answer motivation/why questions"""
        motivation = self.config.get('motivation')
        if motivation:
            return motivation

        # Try to generate with AI
        if self.ai_client:
            return self._ai_answer_question(question, element)

        return self.config.get('default_motivation', 'I am excited about this opportunity and believe my skills align well with the role.')

    def _ai_answer_question(self, question: str, element) -> Optional[str]:
        """Use AI to answer unknown questions"""
        if not self.ai_client:
            return None

        try:
            # Get element type for context
            element_type = element.get_attribute('type') if hasattr(element, 'get_attribute') else 'unknown'

            prompt = f"""You are helping to fill out a job application form. Answer this question professionally and concisely.

Question: {question}
Element type: {element_type}

User's background:
- Name: {self.config.get('first_name', '')} {self.config.get('last_name', '')}
- Current Title: {self.config.get('current_title', 'Software Engineer')}
- Experience: {self.config.get('total_experience_display', '2+ years')}
- Skills: {', '.join(self.config.get('skills', [])[:5])}
- Location: {self.config.get('location', '')}

Provide a direct, professional answer (max 200 characters for short questions, max 500 for long answers).
Do not include any preamble, just the answer."""

            response = self.ai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=150
            )

            answer = response.choices[0].message.content.strip()
            return answer

        except Exception as e:
            print(f"AI answer failed: {e}")
            return None

    def _ai_generate_cover_letter(self) -> Optional[str]:
        """Generate cover letter with AI"""
        if not self.ai_client:
            return None

        try:
            prompt = f"""Generate a professional cover letter for a job application.

Candidate Information:
- Name: {self.config.get('first_name', '')} {self.config.get('last_name', '')}
- Current Title: {self.config.get('current_title', 'Software Engineer')}
- Experience: {self.config.get('total_experience_display', '2+ years')}
- Skills: {', '.join(self.config.get('skills', [])[:10])}
- Education: {self.config.get('education_level', 'Bachelor\'s Degree')} from {self.config.get('university', '')}

Write a concise, professional cover letter (max 250 words) expressing interest in the role and highlighting relevant skills."""

            response = self.ai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.8,
                max_tokens=400
            )

            cover_letter = response.choices[0].message.content.strip()
            return cover_letter

        except Exception as e:
            print(f"AI cover letter generation failed: {e}")
            return None

    def get_answered_questions(self) -> List[Dict]:
        """Get all questions answered so far"""
        return self.answered_questions

    def reset_answered_questions(self):
        """Reset the answered questions list"""
        self.answered_questions = []
