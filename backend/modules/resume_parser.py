"""Resume Parser - Extract text and key information from PDF resume"""
try:
    import PyPDF2
except ImportError:
    PyPDF2 = None
from pathlib import Path
from typing import Dict, List
import re

class ResumeParser:
    """Parse resume PDF and extract relevant information"""

    def __init__(self, resume_path: str = None):
        if resume_path:
            self.resume_path = Path(resume_path)
        else:
            # Default resume location
            self.resume_path = Path(__file__).parent.parent.parent / "deepanshu 2026.pdf"

        self.resume_text = ""
        self.resume_data = {}

        if self.resume_path.exists():
            self.parse_resume()

    def parse_resume(self) -> Dict:
        """Parse PDF and extract text"""
        try:
            with open(self.resume_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)

                # Extract text from all pages
                text_parts = []
                for page in pdf_reader.pages:
                    text_parts.append(page.extract_text())

                self.resume_text = "\n".join(text_parts)

                # Extract structured data
                self.resume_data = self._extract_key_info()

                print(f"Resume parsed successfully ({len(self.resume_text)} characters)")
                return self.resume_data

        except Exception as e:
            print(f"Error parsing resume: {e}")
            return {}

    def _extract_key_info(self) -> Dict:
        """Extract key information from resume text"""
        data = {
            'name': self._extract_name(),
            'email': self._extract_email(),
            'phone': self._extract_phone(),
            'skills': self._extract_skills(),
            'experience_years': self._extract_experience_years(),
            'education': self._extract_education(),
            'recent_companies': self._extract_companies(),
            'technologies': self._extract_technologies(),
            'full_text': self.resume_text
        }
        return data

    def _extract_name(self) -> str:
        """Extract name from resume (usually first line)"""
        lines = self.resume_text.split('\n')
        for line in lines[:5]:  # Check first 5 lines
            line = line.strip()
            if len(line) > 0 and len(line.split()) <= 4 and len(line) < 50:
                # Likely a name
                if not any(char.isdigit() for char in line):
                    return line
        return "Candidate"

    def _extract_email(self) -> str:
        """Extract email address"""
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        match = re.search(email_pattern, self.resume_text)
        return match.group(0) if match else ""

    def _extract_phone(self) -> str:
        """Extract phone number"""
        phone_pattern = r'[\+\d]?[\d\-\.\s\(\)]{10,}'
        match = re.search(phone_pattern, self.resume_text)
        return match.group(0).strip() if match else ""

    def _extract_skills(self) -> List[str]:
        """Extract skills from resume"""
        skills = []

        # Common tech skills to look for
        common_skills = [
            'Python', 'JavaScript', 'TypeScript', 'React', 'Node.js', 'Java',
            'C++', 'SQL', 'MongoDB', 'PostgreSQL', 'AWS', 'Docker', 'Kubernetes',
            'Git', 'API', 'REST', 'GraphQL', 'HTML', 'CSS', 'FastAPI', 'Django',
            'Flask', 'Express', 'Next.js', 'Vue', 'Angular', 'Machine Learning',
            'AI', 'Data Science', 'Selenium', 'Testing', 'CI/CD', 'Agile'
        ]

        text_upper = self.resume_text.upper()
        for skill in common_skills:
            if skill.upper() in text_upper:
                skills.append(skill)

        return skills[:15]  # Top 15 skills

    def _extract_technologies(self) -> List[str]:
        """Extract technologies/frameworks mentioned"""
        # Same as skills for now
        return self._extract_skills()

    def _extract_experience_years(self) -> int:
        """Estimate years of work experience (NOT education years)"""
        import datetime

        text_lower = self.resume_text.lower()
        current_year = datetime.datetime.now().year

        # Find graduation year
        grad_year = None
        # Look for patterns like "Aug 2020 – May 2024" near "University"
        edu_pattern = r'(?:university|college).*?(\d{4})'
        edu_matches = re.findall(edu_pattern, text_lower, re.IGNORECASE)
        if edu_matches:
            # Get the most recent year (likely graduation)
            edu_years = [int(y) for y in edu_matches if 2015 <= int(y) <= 2025]
            if edu_years:
                grad_year = max(edu_years)

        # If graduated in 2024 or later, this is a recent grad
        if grad_year and grad_year >= 2024:
            # Check for internships or work terms
            if 'intern' in text_lower:
                return 1  # Entry-level with internship experience
            return 1  # Recent graduate, less than 1 year

        # Look for WORK EXPERIENCE date ranges (not education)
        # Pattern: "Mar 2025 – Present" or "June 2024 – Dec 2024"
        work_pattern = r'work\s+experience.*?(\d{4})\s*(?:–|-)\s*(?:present|(\d{4}))'
        work_matches = re.findall(work_pattern, text_lower, re.DOTALL | re.IGNORECASE)

        if work_matches:
            total_years = 0
            for match in work_matches:
                start_year = int(match[0])
                end_year = int(match[1]) if match[1] else current_year
                total_years += (end_year - start_year)

            return max(1, min(total_years, 15))  # Cap at 15

        # Fallback: count distinct year mentions in work section only
        work_section_match = re.search(r'work\s+experience(.*?)(?:projects|education|skills|$)', text_lower, re.DOTALL | re.IGNORECASE)
        if work_section_match:
            work_text = work_section_match.group(1)
            work_years = re.findall(r'20\d{2}', work_text)
            if work_years:
                unique_years = sorted(set(int(y) for y in work_years))
                exp_years = max(unique_years) - min(unique_years)
                return max(1, min(exp_years, 10))

        # Default for unknown/recent grad
        return 1

    def _extract_education(self) -> str:
        """Extract education information"""
        education_keywords = ['Bachelor', 'Master', 'PhD', 'B.Tech', 'M.Tech', 'BS', 'MS', 'University', 'College']

        lines = self.resume_text.split('\n')
        for i, line in enumerate(lines):
            if any(keyword.lower() in line.lower() for keyword in education_keywords):
                # Return this line and next 2 lines
                education = ' '.join(lines[i:i+3])
                return education[:200]

        return "Computer Science Degree"

    def _extract_companies(self) -> List[str]:
        """Extract company names from experience"""
        companies = []

        # Simple heuristic: Look for capitalized words after common indicators
        lines = self.resume_text.split('\n')
        for i, line in enumerate(lines):
            if any(word in line.lower() for word in ['experience', 'work', 'employment']):
                # Check next few lines for company names
                for j in range(i+1, min(i+10, len(lines))):
                    words = lines[j].split()
                    if words and words[0][0].isupper() and len(words) <= 5:
                        company = ' '.join(words[:3])
                        if company not in companies:
                            companies.append(company)

        return companies[:3]  # Top 3 companies

    def get_summary(self) -> str:
        """Get a brief summary of the candidate"""
        name = self.resume_data.get('name', 'Candidate')
        skills = ', '.join(self.resume_data.get('skills', [])[:5])
        experience = self.resume_data.get('experience_years', 2)

        summary = f"{name} - {experience}+ years experience in {skills}"
        return summary

    def get_full_text(self) -> str:
        """Get full resume text"""
        return self.resume_text


# Test
if __name__ == "__main__":
    parser = ResumeParser()
    data = parser.resume_data

    print("\n=== RESUME PARSED ===")
    print(f"Name: {data.get('name')}")
    print(f"Email: {data.get('email')}")
    print(f"Phone: {data.get('phone')}")
    print(f"Skills: {', '.join(data.get('skills', []))}")
    print(f"Experience: {data.get('experience_years')} years")
    print(f"Education: {data.get('education')}")
    print(f"\nSummary: {parser.get_summary()}")
