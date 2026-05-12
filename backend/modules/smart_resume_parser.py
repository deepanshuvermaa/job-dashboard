"""
Smart Resume Parser - Extracts data based on actual resume headings
Uses AI to intelligently parse and structure resume content
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Optional
import PyPDF2
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
project_root = Path(__file__).parent.parent.parent
env_path = project_root / '.env'
if env_path.exists():
    load_dotenv(dotenv_path=env_path)


class SmartResumeParser:
    """AI-powered resume parser that adapts to different resume formats"""

    def __init__(self):
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")

        self.openai_client = OpenAI(api_key=api_key)
        self.resume_text = ""
        self.structured_data = {}

    def parse_resume(self, file_path: str) -> Dict:
        """Parse resume and extract structured data using AI"""

        # Extract text from PDF
        self.resume_text = self._extract_text_from_pdf(file_path)

        if not self.resume_text:
            return {
                'error': 'Could not extract text from resume',
                'success': False
            }

        # Use AI to parse the resume intelligently
        self.structured_data = self._ai_parse_resume()

        return {
            'success': True,
            'data': self.structured_data
        }

    def _extract_text_from_pdf(self, file_path: str) -> str:
        """Extract text from PDF file"""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""

                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"

                return text.strip()

        except Exception as e:
            print(f"Error extracting PDF text: {e}")
            return ""

    def _ai_parse_resume(self) -> Dict:
        """Use AI to intelligently parse resume content"""

        prompt = f"""You are an EXPERT resume parser with EXTREME attention to detail. Extract EVERY SINGLE piece of information from this resume.

RESUME TEXT (READ EVERYTHING CAREFULLY):
{self.resume_text}

CRITICAL EXTRACTION RULES:
1. Extract EVERYTHING - Don't summarize, don't skip anything
2. For work experience: Extract EVERY bullet point, EVERY responsibility, EVERY achievement
3. For projects: Extract ALL projects with complete descriptions
4. Calculate experience in MONTHS (not just years)
5. Preserve ALL details, metrics, numbers exactly as written

Extract the following information comprehensively:

1. PERSONAL INFO:
   - Full name
   - Email
   - Phone
   - Location (city, state/country)
   - LinkedIn URL
   - GitHub URL
   - Portfolio website
   - Other links

2. PROFESSIONAL SUMMARY/OBJECTIVE:
   - Extract the full summary/objective section

3. WORK EXPERIENCE (EXTRACT EVERY JOB WITH COMPLETE DETAILS):
   For EACH job position:
   - Exact company name
   - Exact job title
   - Start date (Month Year)
   - End date (Month Year or "Present")
   - Calculate duration in MONTHS (be precise)
   - Extract EVERY SINGLE bullet point as separate items
   - Extract EVERY achievement with exact metrics
   - List ALL technologies/tools mentioned

4. EDUCATION:
   For each degree:
   - Institution name
   - Degree (BS, MS, PhD, etc.)
   - Major/Field of study
   - Graduation year
   - GPA (if mentioned)
   - Relevant coursework
   - Honors/Awards

5. SKILLS:
   Categorize into:
   - Programming languages
   - Frameworks/Libraries
   - Tools & Technologies
   - Soft skills
   - Certifications

6. PROJECTS (EXTRACT ALL PROJECTS):
   For EACH project (don't skip any):
   - Project name
   - COMPLETE description (don't truncate)
   - ALL technologies used
   - Your specific role
   - All outcomes/metrics/results
   - GitHub/demo links if provided

7. ACHIEVEMENTS & AWARDS:
   - List all achievements, awards, scholarships, competitions won

8. CERTIFICATIONS:
   - Certification name
   - Issuing organization
   - Date obtained

9. PUBLICATIONS/RESEARCH:
   - If any research papers, publications, or patents

10. LEADERSHIP & ACTIVITIES:
    - Leadership roles
    - Volunteer work
    - Extracurricular activities

11. LANGUAGES:
    - Languages spoken and proficiency level

IMPORTANT RULES:
- Extract EXACT text from resume - DON'T SUMMARIZE
- Extract ALL bullet points as separate array items
- Calculate experience in MONTHS (not years)
- If section not present, return empty array
- Preserve all details, metrics, numbers exactly
- Return ONLY valid JSON

Return data in this JSON structure (COMPLETE ALL FIELDS):
{{
    "name": "string",
    "email": "string",
    "phone": "string",
    "location": "string",
    "linkedin": "string",
    "github": "string",
    "portfolio": "string",
    "summary": "COMPLETE summary text",
    "experience": [
        {{
            "company": "string",
            "title": "string",
            "start_date": "string",
            "end_date": "string",
            "duration_months": number,
            "duration_display": "X months or Y years Z months",
            "responsibilities": ["EVERY single bullet point as separate item"],
            "achievements": ["EVERY achievement with metrics"],
            "technologies": ["ALL technologies used"]
        }}
    ],
    "projects": [
        {{
            "name": "string",
            "description": "COMPLETE description - DON'T TRUNCATE",
            "technologies": ["ALL technologies"],
            "role": "string",
            "outcomes": ["ALL outcomes/results"],
            "link": "string"
        }}
    ],
    "education": [
        {{
            "institution": "string",
            "degree": "string",
            "major": "string",
            "graduation_year": "string",
            "gpa": "string",
            "honors": ["string"]
        }}
    ],
    "skills": {{
        "programming": ["ALL programming languages"],
        "frameworks": ["ALL frameworks/libraries"],
        "tools": ["ALL tools"],
        "databases": ["ALL databases"],
        "cloud": ["cloud platforms"],
        "soft_skills": ["soft skills"]
    }},
    "achievements": ["ALL achievements"],
    "certifications": [
        {{
            "name": "string",
            "issuer": "string",
            "date": "string"
        }}
    ],
    "publications": ["ALL publications"],
    "leadership": ["ALL leadership roles"],
    "languages": ["spoken languages"],
    "total_experience_months": number,
    "total_experience_display": "X years Y months or Z months",
    "internship_months": number,
    "primary_industry": "string",
    "total_projects_count": number
}}

REMEMBER: Extract EVERYTHING. Better to have complete information than incomplete.
"""

        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert resume parser with extreme attention to detail. Extract EVERY piece of information. Don't summarize or skip anything. Return complete JSON with ALL details."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.1,
                max_tokens=4000,  # Increased for detailed output
                response_format={"type": "json_object"}
            )

            import json
            parsed_data = json.loads(response.choices[0].message.content)

            # Calculate display format if not provided
            if 'total_experience_months' in parsed_data:
                months = parsed_data['total_experience_months']
                years = months // 12
                remaining = months % 12

                if 'total_experience_display' not in parsed_data:
                    if years > 0 and remaining > 0:
                        parsed_data['total_experience_display'] = f"{years} years {remaining} months"
                    elif years > 0:
                        parsed_data['total_experience_display'] = f"{years} years"
                    else:
                        parsed_data['total_experience_display'] = f"{months} months"

                # Keep legacy field for compatibility
                parsed_data['total_experience_years'] = round(months / 12, 1)

            return parsed_data

        except Exception as e:
            print(f"Error in AI parsing: {e}")
            return {
                'error': str(e),
                'success': False
            }

    def update_user_profile(self, user_edits: Dict) -> Dict:
        """Allow user to edit and update the parsed data"""

        # Merge user edits with existing data
        for key, value in user_edits.items():
            if key in self.structured_data:
                self.structured_data[key] = value

        return self.structured_data

    def get_profile_for_content_generation(self) -> Dict:
        """Format the profile data for LinkedIn post generation"""

        # Create a comprehensive profile summary
        profile = {
            'name': self.structured_data.get('name', ''),
            'title': self.structured_data.get('experience', [{}])[0].get('title', 'Professional'),
            'industry': self.structured_data.get('primary_industry', 'Technology'),
            'experience_years': self.structured_data.get('total_experience_years', 1),
            'summary': self.structured_data.get('summary', ''),

            # Top skills
            'top_skills': (
                self.structured_data.get('skills', {}).get('programming', [])[:5] +
                self.structured_data.get('skills', {}).get('frameworks', [])[:3]
            ),

            # Key achievements (top 5)
            'achievements': self.structured_data.get('achievements', [])[:5],

            # Recent companies
            'companies': [
                exp.get('company', '')
                for exp in self.structured_data.get('experience', [])[:3]
            ],

            # Projects
            'projects': [
                {
                    'name': p.get('name', ''),
                    'description': p.get('description', ''),
                    'technologies': p.get('technologies', [])
                }
                for p in self.structured_data.get('projects', [])[:3]
            ],

            # Education
            'education': self.structured_data.get('education', []),

            # All achievements with metrics
            'detailed_achievements': [
                achievement
                for exp in self.structured_data.get('experience', [])
                for achievement in exp.get('achievements', [])
            ],

            # Leadership
            'leadership': self.structured_data.get('leadership', []),

            # Full structured data
            'full_data': self.structured_data
        }

        return profile


# Test function
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python smart_resume_parser.py <path_to_resume.pdf>")
        sys.exit(1)

    parser = SmartResumeParser()
    result = parser.parse_resume(sys.argv[1])

    if result.get('success'):
        import json
        print(json.dumps(result['data'], indent=2))
    else:
        print(f"Error: {result.get('error')}")
