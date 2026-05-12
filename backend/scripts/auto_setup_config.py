"""
Automatic User Configuration Setup
Populates user_config from resume and .env file
"""

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
from config.user_config import UserConfig

# Load .env
env_path = Path(__file__).parent.parent.parent / '.env'
load_dotenv(env_path)

def auto_setup():
    """Auto-populate user config from available data"""

    config = UserConfig()

    print("\n[SETUP] Auto-configuring user profile...\n")

    # Get data from environment
    linkedin_email = os.getenv('LINKEDIN_EMAIL', '')
    linkedin_password = os.getenv('LINKEDIN_PASSWORD', '')
    openai_key = os.getenv('OPENAI_API_KEY', '')
    github_token = os.getenv('GITHUB_TOKEN', '')
    github_username = os.getenv('GITHUB_USERNAME', '')

    # Try to get resume path from common locations
    resume_path = None
    common_paths = [
        Path(__file__).parent.parent.parent / "deepanshu 2026.pdf",
        Path(__file__).parent.parent / "uploads" / "deepanshu 2026.pdf",
    ]

    for path in common_paths:
        if path.exists():
            resume_path = str(path)
            break

    # Parse resume if found
    resume_data = {}
    if resume_path:
        print(f"[OK] Found resume: {resume_path}")
        try:
            from modules.smart_resume_parser import SmartResumeParser
            parser = SmartResumeParser()
            result = parser.parse_resume(resume_path)
            if result.get('success'):
                resume_data = result['data']
                print(f"[OK] Parsed resume successfully")
        except Exception as e:
            print(f"[WARN] Could not parse resume: {e}")

    # Configure personal section
    personal = {}
    if resume_data:
        personal = {
            'first_name': resume_data.get('name', '').split()[0] if resume_data.get('name') else '',
            'last_name': ' '.join(resume_data.get('name', '').split()[1:]) if resume_data.get('name') else '',
            'email': resume_data.get('email', ''),
            'phone': resume_data.get('phone', ''),
            'location': resume_data.get('location', ''),
            'linkedin_url': resume_data.get('linkedin_url', ''),
            'github_url': resume_data.get('github_url', ''),
        }

    # Fallback to defaults if no resume
    if not personal.get('email'):
        personal['email'] = linkedin_email
    if not personal.get('first_name'):
        personal['first_name'] = 'User'
    if not personal.get('last_name'):
        personal['last_name'] = 'Name'
    if not personal.get('phone'):
        personal['phone'] = '+1234567890'
    if not personal.get('location'):
        personal['location'] = 'United States'

    config.update_section('personal', personal)
    print(f"[OK] Configured personal info: {personal.get('first_name')} {personal.get('last_name')}")

    # Configure professional section
    professional = {}
    if resume_data:
        experiences = resume_data.get('experience', [])
        if experiences:
            latest_exp = experiences[0]
            professional = {
                'current_company': latest_exp.get('company', ''),
                'current_title': latest_exp.get('title', ''),
                'years_of_experience': resume_data.get('total_experience_years', 0),
                'skills': resume_data.get('skills', {}).get('programming', [])[:10],
                'industry': resume_data.get('primary_industry', 'Technology')
            }

    # Fallback
    if not professional.get('current_title'):
        professional['current_title'] = 'Software Engineer'
    if not professional.get('years_of_experience'):
        professional['years_of_experience'] = 2
    if not professional.get('skills'):
        professional['skills'] = ['Python', 'JavaScript', 'React', 'Node.js']

    config.update_section('professional', professional)
    print(f"[OK] Configured professional info: {professional.get('current_title')} with {professional.get('years_of_experience')} years exp")

    # Configure education
    education = {}
    if resume_data and resume_data.get('education'):
        edu = resume_data['education'][0] if resume_data['education'] else {}
        education = {
            'education_level': edu.get('degree', "Bachelor's Degree"),
            'university': edu.get('institution', ''),
            'graduation_year': str(edu.get('end_year', ''))
        }

    if not education.get('education_level'):
        education['education_level'] = "Bachelor's Degree"

    config.update_section('education', education)
    print(f"[OK] Configured education: {education.get('education_level')}")

    # Configure work status
    work_status = {
        'work_authorization': 'Yes',
        'requires_visa_sponsorship': 'No',
        'currently_employed': 'Yes',
        'notice_period': '2 weeks',
        'willing_to_relocate': 'Yes'
    }
    config.update_section('work_status', work_status)
    print(f"[OK] Configured work status")

    # Configure compensation
    compensation = {
        'expected_salary': '150000',
        'currency': 'USD'
    }
    config.update_section('compensation', compensation)
    print(f"[OK] Configured compensation")

    # Configure application settings
    application = {
        'resume_path': resume_path or '',
        'auto_follow_companies': False,
        'max_applications_per_day': 50
    }
    config.update_section('application', application)
    print(f"[OK] Configured application settings")

    # Configure LinkedIn credentials
    linkedin = {
        'email': linkedin_email,
        'password': linkedin_password,
        'chrome_user_data_dir': ''
    }
    config.update_section('linkedin', linkedin)
    print(f"[OK] Configured LinkedIn credentials")

    # Configure AI
    ai = {
        'primary_provider': 'openai',
        'fallback_providers': ['openai'],
        'openai_api_key': openai_key,
        'openai_model': 'gpt-3.5-turbo'
    }
    config.update_section('ai', ai)
    print(f"[OK] Configured AI provider")

    # Save configuration
    config.save()

    print("\n[SUCCESS] Configuration saved successfully!\n")

    # Validate
    issues = config.validate()
    if config.is_valid():
        print("[SUCCESS] Configuration is VALID and ready for Auto-Apply!\n")
    else:
        print("[WARN] Configuration has some issues:")
        if issues['missing']:
            print(f"  Missing: {issues['missing']}")
        if issues['invalid']:
            print(f"  Invalid: {issues['invalid']}")
        print()

    return config

if __name__ == '__main__':
    auto_setup()
