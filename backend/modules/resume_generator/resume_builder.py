"""
ATS-Optimized Resume Builder
Generates tailored PDF resumes with:
- Keyword injection from job descriptions
- Archetype-based template selection
- Dynamic experience reordering by relevance
- Single-column ATS-safe layout
"""

import os
import json
from typing import Dict, List, Optional
from datetime import datetime
from pathlib import Path
from string import Template


class ResumeBuilder:
    """Generate ATS-optimized PDF resumes tailored to specific jobs"""

    ARCHETYPES = {
        'general': {
            'name': 'General / Balanced',
            'emphasis': ['full-stack', 'software engineering', 'problem solving'],
        },
        'full_stack': {
            'name': 'Full Stack Developer',
            'emphasis': ['react', 'node.js', 'frontend', 'backend', 'api'],
        },
        'backend': {
            'name': 'Backend Engineer',
            'emphasis': ['python', 'api', 'database', 'microservices', 'infrastructure'],
        },
        'frontend': {
            'name': 'Frontend Developer',
            'emphasis': ['react', 'typescript', 'css', 'ui/ux', 'responsive'],
        },
        'data': {
            'name': 'Data Engineer / Scientist',
            'emphasis': ['python', 'sql', 'data pipeline', 'machine learning', 'analytics'],
        },
        'devops': {
            'name': 'DevOps / SRE',
            'emphasis': ['docker', 'kubernetes', 'ci/cd', 'aws', 'terraform', 'monitoring'],
        },
    }

    def __init__(self, user_profile: Dict = None):
        self.profile = user_profile or self._load_user_profile()
        self.template_dir = Path(__file__).parent / "templates"
        self.output_dir = Path(__file__).parent.parent.parent / "data" / "resumes"
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def _load_user_profile(self) -> Dict:
        """Load user profile from config"""
        config_path = Path(__file__).parent.parent.parent / "data" / "user_config.json"
        if config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {
            'name': 'Your Name',
            'email': 'your.email@example.com',
            'phone': '+1 (555) 000-0000',
            'location': 'Remote',
            'linkedin': 'linkedin.com/in/yourprofile',
            'github': 'github.com/yourprofile',
            'summary': 'Experienced software engineer with expertise in building scalable applications.',
            'skills': ['Python', 'JavaScript', 'React', 'Node.js', 'AWS', 'Docker', 'PostgreSQL'],
            'experience': [],
            'education': [],
            'certifications': [],
        }

    def generate(
        self,
        job: Dict,
        keywords: List[str],
        archetype: str = 'general',
        page_format: str = 'Letter'
    ) -> str:
        """
        Generate a tailored ATS-optimized resume PDF.
        Returns the path to the generated PDF file.
        """
        # Auto-detect archetype if set to general
        if archetype == 'general' or archetype == 'auto':
            archetype = self._detect_archetype(job)

        import re as _re
        # Sanitize company and title for safe filenames (remove newlines, special chars)
        company = _re.sub(r'[^\w\s-]', '', job.get('company', 'Unknown').replace('\n', ' ')).strip().replace(' ', '_')[:30]
        title = _re.sub(r'[^\w\s-]', '', job.get('title', 'Job').replace('\n', ' ')).strip().replace(' ', '_')[:30]
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"Resume_{company}_{title}_{timestamp}"

        # Reorder experience by relevance to job
        reordered_experience = self._reorder_experience(
            self.profile.get('experience', []),
            job, keywords
        )

        # Tailor bullet points to emphasize JD keywords
        tailored_experience = self._tailor_bullets(reordered_experience, job, keywords)

        # Tailor projects too
        tailored_projects = self._tailor_bullets(
            self.profile.get('projects', []), job, keywords, is_project=True
        )

        # Generate JD-tailored summary
        tailored_summary = self._tailor_summary(job, keywords, archetype)

        # Inject keywords into skills section
        enhanced_skills = self._enhance_skills(self.profile.get('skills', []), keywords)

        # Build tailored profile
        tailored_profile = {**self.profile}
        tailored_profile['summary'] = tailored_summary
        tailored_profile['projects'] = tailored_projects

        # Build HTML from template
        html_content = self._render_html(
            profile=tailored_profile,
            job=job,
            keywords=keywords,
            archetype=archetype,
            experience=tailored_experience,
            skills=enhanced_skills,
            page_format=page_format
        )

        # Save HTML version
        html_path = self.output_dir / f"{filename}.html"
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html_content)

        # Try to convert to PDF
        pdf_path = self.output_dir / f"{filename}.pdf"
        try:
            self._html_to_pdf(str(html_path), str(pdf_path))
            print(f"  [Resume] Generated PDF: {pdf_path}")
            return str(pdf_path)
        except Exception as e:
            print(f"  [Resume] PDF conversion failed ({e}), HTML saved: {html_path}")
            return str(html_path)

    def _detect_archetype(self, job: Dict) -> str:
        """Auto-detect the best archetype based on job description"""
        desc = (job.get('description_snippet', '') + ' ' + job.get('title', '')).lower()

        scores = {}
        for arch_id, arch_info in self.ARCHETYPES.items():
            score = sum(1 for term in arch_info['emphasis'] if term in desc)
            scores[arch_id] = score

        best = max(scores, key=scores.get) if scores else 'general'
        return best if scores.get(best, 0) > 0 else 'general'

    def _reorder_experience(self, experience: List[Dict], job: Dict, keywords: List[str]) -> List[Dict]:
        """Reorder experience entries to put most relevant first"""
        if not experience:
            return experience

        job_text = (job.get('title', '') + ' ' + job.get('description_snippet', '')).lower()
        keywords_lower = {k.lower() for k in keywords}

        def relevance_score(exp):
            text = (
                exp.get('title', '') + ' ' +
                exp.get('company', '') + ' ' +
                ' '.join(exp.get('bullets', []))
            ).lower()
            score = 0
            for kw in keywords_lower:
                if kw in text:
                    score += 2
            for word in job_text.split():
                if word in text and len(word) > 3:
                    score += 0.5
            return score

        return sorted(experience, key=relevance_score, reverse=True)

    def _tailor_summary(self, job: Dict, keywords: List[str], archetype: str) -> str:
        """Generate a JD-tailored professional summary"""
        job_title = job.get('title', '')
        company = job.get('company', '')
        desc = job.get('description_snippet', '').lower()

        # Pick relevant emphasis based on JD
        tech_highlights = []
        for kw in keywords[:6]:
            if kw.lower() not in ['bachelor', 'master', 'bs', 'ms', 'computer science']:
                tech_highlights.append(kw)

        tech_str = ', '.join(tech_highlights[:4]) if tech_highlights else 'modern web technologies'

        # Build tailored summary
        base = self.profile.get('summary', '')

        # Create a JD-specific opening
        if company and company != 'Company':
            opener = f"Results-driven Full Stack Engineer with hands-on experience in {tech_str}, seeking to contribute to {company}"
            if job_title:
                opener += f" as {job_title}"
            opener += "."
        else:
            opener = f"Results-driven Full Stack Engineer with deep expertise in {tech_str}."

        # Add quantified achievements
        achievements = []
        if 'saas' in desc or 'platform' in desc:
            achievements.append("Built production-grade SaaS platforms scaled to 100+ users with recurring revenue")
        if 'automation' in desc or 'automat' in desc:
            achievements.append("Automated workflows reducing manual effort by 95% and increasing team productivity")
        if 'api' in desc or 'backend' in desc:
            achievements.append("Designed and deployed RESTful APIs and microservices handling high-throughput workloads")
        if 'cloud' in desc or 'aws' in desc or 'deploy' in desc:
            achievements.append("Deployed cloud-native applications on AWS/GCP with CI/CD pipelines")
        if 'ai' in desc or 'ml' in desc or 'machine learning' in desc:
            achievements.append("Integrated AI/ML models into production systems generating measurable revenue impact")
        if not achievements:
            achievements.append("Proven track record of delivering scalable software solutions with measurable business impact")

        return f"{opener} {'. '.join(achievements[:2])}. Passionate about building impactful products with clean, maintainable code."

    def _tailor_bullets(self, entries: List[Dict], job: Dict, keywords: List[str], is_project: bool = False) -> List[Dict]:
        """Tailor bullet points to emphasize JD-relevant keywords and achievements"""
        import re as _re
        desc = (job.get('description_snippet', '') + ' ' + job.get('title', '')).lower()
        keywords_lower = {k.lower() for k in keywords}

        tailored = []
        for entry in entries:
            new_entry = {**entry}
            new_bullets = []

            for bullet in entry.get('bullets', []):
                new_bullet = bullet

                # Bold keywords that appear in the bullet (HTML bold for emphasis)
                for kw in keywords:
                    if kw.lower() in new_bullet.lower() and len(kw) > 2:
                        # Case-insensitive replace with bold
                        pattern = _re.compile(_re.escape(kw), _re.IGNORECASE)
                        new_bullet = pattern.sub(f'<strong>{kw}</strong>', new_bullet, count=1)

                # Add quantified metrics if bullet doesn't have numbers
                if not _re.search(r'\d+%|\$\d+|\d+x|\d+ user', new_bullet.lower()):
                    # Try to add relevant metrics based on JD context
                    if 'scalab' in desc and ('platform' in new_bullet.lower() or 'system' in new_bullet.lower()):
                        new_bullet = new_bullet.rstrip('.') + ', handling scalable workloads.'
                    elif 'performance' in desc and 'built' in new_bullet.lower():
                        new_bullet = new_bullet.rstrip('.') + ', optimizing for performance and reliability.'

                new_bullets.append(new_bullet)

            # If this entry has few relevant keywords, add a context line
            entry_text = ' '.join(new_bullets).lower()
            matching_kws = [kw for kw in keywords_lower if kw in entry_text]

            # Reorder bullets: most keyword-rich first
            def bullet_relevance(b):
                b_lower = b.lower()
                return sum(1 for kw in keywords_lower if kw in b_lower)

            new_bullets.sort(key=bullet_relevance, reverse=True)

            new_entry['bullets'] = new_bullets
            tailored.append(new_entry)

        return tailored

    def _enhance_skills(self, user_skills: List[str], job_keywords: List[str]) -> List[str]:
        """Add matching job keywords to skills list and prioritize them"""
        skills_lower = {s.lower() for s in user_skills}
        enhanced = list(user_skills)

        # Add keywords that aren't already in user skills
        for kw in job_keywords:
            if kw.lower() not in skills_lower and len(kw) > 2:
                # Only add technical-sounding keywords
                if any(c.isalpha() for c in kw):
                    enhanced.append(kw)

        return enhanced[:25]  # Limit total skills

    def _render_html(
        self,
        profile: Dict,
        job: Dict,
        keywords: List[str],
        archetype: str,
        experience: List[Dict],
        skills: List[str],
        page_format: str = 'Letter'
    ) -> str:
        """Render the resume as professional ATS-optimized HTML"""
        if page_format == 'A4':
            page_width, page_height = '210mm', '297mm'
        else:
            page_width, page_height = '8.5in', '11in'

        # Build experience HTML
        experience_html = ''
        for exp in experience:
            bullets = ''.join(f'<li>{b}</li>' for b in exp.get('bullets', []))
            experience_html += f"""
            <div class="entry">
                <div class="entry-header">
                    <div><strong class="entry-title">{exp.get('title', '')}</strong> <span class="entry-sep">|</span> <span class="entry-org">{exp.get('company', '')}</span></div>
                    <span class="entry-date">{exp.get('date_range', '')}</span>
                </div>
                <ul>{bullets}</ul>
            </div>"""

        # Build projects HTML
        projects_html = ''
        for proj in profile.get('projects', []):
            bullets = ''.join(f'<li>{b}</li>' for b in proj.get('bullets', []))
            tech = proj.get('tech', '')
            projects_html += f"""
            <div class="entry">
                <div class="entry-header">
                    <div><strong class="entry-title">{proj.get('name', '')}</strong> {f'<span class="tech-tag">{tech}</span>' if tech else ''}</div>
                </div>
                <ul>{bullets}</ul>
            </div>"""

        # Build grouped skills HTML
        skills_grouped = {}
        skill_categories = {
            'Languages': ['python', 'javascript', 'c++', 'html/css', 'sql', 'typescript', 'java', 'go', 'rust'],
            'Frameworks': ['react', 'node.js', 'express', 'react native', 'flutter', 'next.js', 'django', 'flask', 'fastapi'],
            'Cloud & DevOps': ['aws', 'gcp', 'docker', 'ci/cd', 'kubernetes', 'terraform'],
            'Tools': ['git', 'postman', 'figma', 'powerbi', 'mongodb', 'postgresql', 'redis'],
            'Concepts': ['saas architecture', 'rbac', 'ai automation', 'web scraping', 'rest api', 'microservices', 'agile'],
        }
        remaining_skills = list(skills)
        for cat, cat_keywords in skill_categories.items():
            matched = [s for s in remaining_skills if s.lower() in cat_keywords]
            if matched:
                skills_grouped[cat] = matched
                remaining_skills = [s for s in remaining_skills if s not in matched]
        if remaining_skills:
            skills_grouped['Other'] = remaining_skills

        skills_html = ''
        for cat, cat_skills in skills_grouped.items():
            skills_html += f'<div class="skill-row"><strong>{cat}:</strong> {", ".join(cat_skills)}</div>'

        # Build education HTML
        education_html = ''
        for edu in profile.get('education', []):
            gpa = edu.get('gpa', '')
            education_html += f"""
            <div class="entry-header" style="margin-bottom:4px">
                <div><strong>{edu.get('degree', '')}</strong> <span class="entry-sep">-</span> {edu.get('school', '')} {f'<span class="gpa">({gpa})</span>' if gpa else ''}</div>
                <span class="entry-date">{edu.get('year', '')}</span>
            </div>"""

        # Tailored summary based on job
        job_title = job.get('title', '')
        company = job.get('company', '')
        summary = profile.get('summary', '')
        if job_title and company and company != 'Company':
            summary = f"Full Stack Engineer seeking the {job_title} role at {company}. {summary}"

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Resume - {profile.get('name', '')} - {company}</title>
<style>
@page {{ size: {page_width} {page_height}; margin: 0.5in 0.6in; }}
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{
    font-family: 'Georgia', 'Cambria', 'Times New Roman', serif;
    font-size: 10pt;
    line-height: 1.45;
    color: #222;
    max-width: {page_width};
    padding: 0;
}}
/* Header */
.header {{ text-align: center; padding-bottom: 10px; margin-bottom: 14px; border-bottom: 2px solid #1a365d; }}
.header h1 {{ font-size: 22pt; color: #1a365d; font-weight: 700; letter-spacing: 1px; margin-bottom: 5px; font-family: 'Calibri', 'Helvetica Neue', Arial, sans-serif; }}
.header .subtitle {{ font-size: 11pt; color: #4a5568; font-style: italic; margin-bottom: 6px; }}
.header .contact {{ font-size: 9pt; color: #4a5568; }}
.header .contact a {{ color: #2b6cb0; text-decoration: none; }}
.header .contact .sep {{ margin: 0 6px; color: #cbd5e0; }}

/* Sections */
.section {{ margin-bottom: 14px; }}
.section h2 {{
    font-family: 'Calibri', 'Helvetica Neue', Arial, sans-serif;
    font-size: 11pt; color: #1a365d; text-transform: uppercase;
    letter-spacing: 1.5px; font-weight: 700;
    border-bottom: 1px solid #e2e8f0; padding-bottom: 3px; margin-bottom: 8px;
}}

/* Summary */
.summary {{ font-size: 9.5pt; color: #333; line-height: 1.5; }}

/* Skills */
.skill-row {{ font-size: 9.5pt; margin-bottom: 3px; line-height: 1.5; }}
.skill-row strong {{ color: #1a365d; font-size: 9.5pt; }}

/* Entries (experience, projects) */
.entry {{ margin-bottom: 10px; }}
.entry-header {{
    display: flex; justify-content: space-between; align-items: baseline;
    margin-bottom: 2px;
}}
.entry-title {{ font-size: 10.5pt; color: #1a365d; }}
.entry-sep {{ color: #a0aec0; margin: 0 4px; }}
.entry-org {{ color: #4a5568; font-style: italic; }}
.entry-date {{ font-size: 9pt; color: #718096; white-space: nowrap; font-style: italic; }}
.tech-tag {{ font-size: 8.5pt; color: #5a67d8; background: #ebf4ff; padding: 1px 6px; border-radius: 3px; margin-left: 6px; }}
.gpa {{ font-size: 9pt; color: #718096; }}

/* Lists */
ul {{ padding-left: 16px; margin-top: 3px; }}
li {{ font-size: 9.5pt; margin-bottom: 2px; line-height: 1.4; color: #333; }}
</style>
</head>
<body>

<div class="header">
    <h1>{profile.get('name', 'Your Name')}</h1>
    <div class="subtitle">Full Stack Engineer</div>
    <div class="contact">
        {profile.get('email', '')}
        <span class="sep">|</span>{profile.get('phone', '')}
        <span class="sep">|</span>{profile.get('location', '')}
        {f'<span class="sep">|</span><a href="https://{profile.get("linkedin", "")}">{profile.get("linkedin", "")}</a>' if profile.get('linkedin') else ''}
        {f'<span class="sep">|</span><a href="https://{profile.get("github", "")}">{profile.get("github", "")}</a>' if profile.get('github') else ''}
    </div>
</div>

<div class="section">
    <h2>Professional Summary</h2>
    <p class="summary">{summary}</p>
</div>

<div class="section">
    <h2>Technical Skills</h2>
    {skills_html}
</div>

{"<div class='section'><h2>Professional Experience</h2>" + experience_html + "</div>" if experience_html else ""}

{"<div class='section'><h2>Projects & SaaS Products</h2>" + projects_html + "</div>" if projects_html else ""}

{"<div class='section'><h2>Education</h2>" + education_html + "</div>" if education_html else ""}

</body>
</html>"""

        return html

    def _html_to_pdf(self, html_path: str, pdf_path: str):
        """Convert HTML to PDF using available tools"""
        # Try WeasyPrint first
        try:
            from weasyprint import HTML
            HTML(filename=html_path).write_pdf(pdf_path)
            return
        except ImportError:
            pass

        # Try Playwright
        try:
            from playwright.sync_api import sync_playwright
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                page.goto(f'file:///{html_path.replace(chr(92), "/")}')
                page.pdf(path=pdf_path, format='Letter', print_background=True)
                browser.close()
            return
        except ImportError:
            pass

        # If no PDF tool available, just keep the HTML
        raise RuntimeError("No PDF converter available (install weasyprint or playwright)")
