"""
User Configuration System
Stores personal information, preferences, and application settings
Based on GodsScion's approach with enhancements
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional


class UserConfig:
    """Manage user configuration for LinkedIn automation"""

    def __init__(self, config_file: str = None):
        """
        Initialize user configuration

        Args:
            config_file: Path to JSON config file
        """
        self.config_file = config_file or self._get_default_config_path()
        self.config = self._load_config()

    def _get_default_config_path(self) -> str:
        """Get default config file path"""
        config_dir = Path(__file__).parent.parent / "data"
        config_dir.mkdir(exist_ok=True)
        return str(config_dir / "user_config.json")

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading config: {e}")
                return self._get_default_config()
        else:
            return self._get_default_config()

    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration"""
        return {
            # Personal Information
            "personal": {
                "first_name": "",
                "last_name": "",
                "email": "",
                "phone": "",
                "location": "",
                "city": "",
                "state": "",
                "zip_code": "",
                "linkedin_url": "",
                "portfolio_url": "",
                "github_url": "",
                "website": ""
            },

            # Professional Information
            "professional": {
                "current_company": "",
                "current_title": "",
                "desired_title": "",
                "years_of_experience": 0,
                "total_experience_display": "",
                "total_experience_months": 0,
                "industry": "",
                "skills": [],
                "certifications": [],
                "languages": ["English"]
            },

            # Education
            "education": {
                "education_level": "Bachelor's Degree",
                "university": "",
                "degree": "",
                "major": "",
                "graduation_year": "",
                "gpa": ""
            },

            # Work Authorization & Availability
            "work_status": {
                "work_authorization": "Yes",
                "requires_visa_sponsorship": "No",
                "currently_employed": "Yes",
                "notice_period": "2 weeks",
                "availability": "Immediate",
                "willing_to_relocate": "Yes",
                "willing_to_travel": "Yes",
                "remote_preference": "Remote"
            },

            # Compensation
            "compensation": {
                "current_salary": "",
                "expected_salary": "",
                "desired_salary": "",
                "salary_negotiable": "Yes",
                "currency": "USD"
            },

            # Application Preferences
            "application": {
                "resume_path": "",
                "cover_letter": "",
                "motivation": "I am excited about this opportunity and believe my skills align well with the role.",
                "default_yes_no_answer": "Yes",
                "auto_follow_companies": False,
                "auto_connect_hr": False,
                "max_applications_per_day": 50,
                "delay_between_applications": 5
            },

            # LinkedIn Credentials (for automation)
            "linkedin": {
                "email": "",
                "password": "",
                "chrome_user_data_dir": ""
            },

            # AI Provider Configuration
            "ai": {
                "primary_provider": "openai",
                "fallback_providers": ["openai", "deepseek", "gemini"],
                "openai_api_key": os.getenv('OPENAI_API_KEY', ''),
                "openai_model": "gpt-3.5-turbo",
                "deepseek_api_key": os.getenv('DEEPSEEK_API_KEY', ''),
                "deepseek_model": "deepseek-chat",
                "gemini_api_key": os.getenv('GEMINI_API_KEY', ''),
                "gemini_model": "gemini-1.5-flash"
            },

            # Job Search Filters
            "job_search": {
                "keywords": ["Software Engineer", "Full Stack Developer"],
                "locations": ["United States"],
                "job_types": ["Full-time"],
                "experience_levels": ["Mid-Senior level"],
                "remote_filter": "Remote",
                "date_posted": "Past Week",
                "easy_apply_only": True,
                "company_blacklist": [],
                "keyword_blacklist": [],
                "min_salary": 0,
                "max_applications": 50
            },

            # Custom Answers for Common Questions
            "question_answers": {
                # These will override pattern-based answers
                "custom_answers": {}
            }
        }

    def save(self):
        """Save configuration to file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, indent=2, fp=f)
            print(f"[OK] Configuration saved to {self.config_file}")
            return True
        except Exception as e:
            print(f"[ERROR] Error saving config: {e}")
            return False

    def get(self, key_path: str, default=None):
        """
        Get configuration value by dot-separated key path

        Examples:
            config.get('personal.first_name')
            config.get('ai.openai_api_key')
        """
        keys = key_path.split('.')
        value = self.config

        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default

        return value

    def set(self, key_path: str, value: Any):
        """
        Set configuration value by dot-separated key path

        Examples:
            config.set('personal.first_name', 'John')
            config.set('ai.openai_api_key', 'sk-...')
        """
        keys = key_path.split('.')
        target = self.config

        # Navigate to the parent dict
        for key in keys[:-1]:
            if key not in target:
                target[key] = {}
            target = target[key]

        # Set the final value
        target[keys[-1]] = value

    def update(self, updates: Dict[str, Any]):
        """Update multiple configuration values"""
        for key_path, value in updates.items():
            self.set(key_path, value)

    def get_all(self) -> Dict[str, Any]:
        """Get entire configuration"""
        return self.config.copy()

    def get_section(self, section: str) -> Dict[str, Any]:
        """Get entire configuration section"""
        return self.config.get(section, {}).copy()

    def update_section(self, section: str, updates: Dict[str, Any]):
        """Update entire section"""
        if section in self.config:
            self.config[section].update(updates)
        else:
            self.config[section] = updates

    def get_flat_config(self) -> Dict[str, Any]:
        """
        Get flattened configuration for QuestionAnswerer

        Returns a flat dictionary with all values accessible by simple keys
        """
        flat = {}

        # Personal info
        personal = self.get_section('personal')
        flat.update(personal)

        # Professional info
        professional = self.get_section('professional')
        flat.update(professional)

        # Education
        education = self.get_section('education')
        flat.update(education)

        # Work status
        work_status = self.get_section('work_status')
        flat.update(work_status)

        # Compensation
        compensation = self.get_section('compensation')
        flat.update(compensation)

        # Application preferences
        application = self.get_section('application')
        flat.update(application)

        # LinkedIn credentials
        linkedin = self.get_section('linkedin')
        flat['linkedin_email'] = linkedin.get('email', '')
        flat['linkedin_password'] = linkedin.get('password', '')
        flat['chrome_user_data_dir'] = linkedin.get('chrome_user_data_dir', '')

        return flat

    def validate(self) -> Dict[str, List[str]]:
        """
        Validate configuration and return missing/invalid fields

        Returns:
            Dictionary with 'missing' and 'invalid' lists
        """
        issues = {
            'missing': [],
            'invalid': []
        }

        # Check required personal fields
        required_personal = ['first_name', 'last_name', 'email', 'phone', 'location']
        for field in required_personal:
            if not self.get(f'personal.{field}'):
                issues['missing'].append(f'personal.{field}')

        # Check resume path
        resume_path = self.get('application.resume_path')
        if resume_path and not os.path.exists(resume_path):
            issues['invalid'].append('application.resume_path (file not found)')

        # Check AI provider config
        primary_provider = self.get('ai.primary_provider', 'openai')
        api_key = self.get(f'ai.{primary_provider}_api_key')
        if not api_key:
            issues['missing'].append(f'ai.{primary_provider}_api_key')

        return issues

    def is_valid(self) -> bool:
        """Check if configuration is valid"""
        issues = self.validate()
        return not issues['missing'] and not issues['invalid']

    def print_validation_report(self):
        """Print validation report"""
        issues = self.validate()

        if self.is_valid():
            print("[OK] Configuration is valid")
            return

        print("\n[WARN] Configuration Issues:\n")

        if issues['missing']:
            print("Missing required fields:")
            for field in issues['missing']:
                print(f"  - {field}")

        if issues['invalid']:
            print("\nInvalid fields:")
            for field in issues['invalid']:
                print(f"  - {field}")

        print()

    def export_to_file(self, filepath: str):
        """Export configuration to specific file"""
        try:
            with open(filepath, 'w') as f:
                json.dump(self.config, indent=2, fp=f)
            print(f"[OK] Configuration exported to {filepath}")
            return True
        except Exception as e:
            print(f"[ERROR] Export failed: {e}")
            return False

    def import_from_file(self, filepath: str):
        """Import configuration from file"""
        try:
            with open(filepath, 'r') as f:
                imported_config = json.load(f)

            # Merge with default config to ensure all keys exist
            default = self._get_default_config()
            self._deep_merge(default, imported_config)
            self.config = default

            print(f"[OK] Configuration imported from {filepath}")
            return True
        except Exception as e:
            print(f"[ERROR] Import failed: {e}")
            return False

    def _deep_merge(self, base: Dict, updates: Dict):
        """Deep merge updates into base dictionary"""
        for key, value in updates.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._deep_merge(base[key], value)
            else:
                base[key] = value


# Global user config instance
user_config = UserConfig()
