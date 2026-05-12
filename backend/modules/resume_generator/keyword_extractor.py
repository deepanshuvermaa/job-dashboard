"""
Keyword Extractor - Extracts 15-20 key terms from job descriptions
that should appear in the tailored resume for ATS optimization.
"""

import re
from typing import List, Dict, Optional
from collections import Counter


# Common tech skills and keywords grouped by category
TECH_SKILLS = {
    'languages': ['python', 'javascript', 'typescript', 'java', 'go', 'golang', 'rust', 'c++', 'c#',
                  'ruby', 'php', 'swift', 'kotlin', 'scala', 'r', 'sql', 'html', 'css', 'sass'],
    'frontend': ['react', 'vue', 'angular', 'next.js', 'nextjs', 'svelte', 'tailwind', 'bootstrap',
                 'redux', 'webpack', 'vite', 'graphql', 'rest api', 'responsive design'],
    'backend': ['node.js', 'nodejs', 'express', 'fastapi', 'django', 'flask', 'spring boot',
                'rails', 'asp.net', 'microservices', 'api design', 'grpc'],
    'cloud': ['aws', 'azure', 'gcp', 'google cloud', 'heroku', 'vercel', 'netlify', 'digitalocean',
              'lambda', 's3', 'ec2', 'cloudformation', 'terraform', 'pulumi'],
    'data': ['postgresql', 'mysql', 'mongodb', 'redis', 'elasticsearch', 'dynamodb', 'cassandra',
             'kafka', 'rabbitmq', 'spark', 'airflow', 'snowflake', 'bigquery', 'data pipeline'],
    'devops': ['docker', 'kubernetes', 'k8s', 'ci/cd', 'jenkins', 'github actions', 'gitlab ci',
               'ansible', 'prometheus', 'grafana', 'helm', 'argocd', 'infrastructure as code'],
    'ai_ml': ['machine learning', 'deep learning', 'nlp', 'computer vision', 'pytorch', 'tensorflow',
              'scikit-learn', 'hugging face', 'llm', 'openai', 'langchain', 'rag', 'fine-tuning'],
    'practices': ['agile', 'scrum', 'kanban', 'tdd', 'code review', 'pair programming',
                  'design patterns', 'clean code', 'solid', 'ddd', 'event-driven'],
    'soft': ['leadership', 'mentoring', 'cross-functional', 'stakeholder', 'communication',
             'problem-solving', 'collaboration', 'ownership', 'impact'],
}

# Flatten all keywords for quick lookup
ALL_KEYWORDS = {}
for category, keywords in TECH_SKILLS.items():
    for kw in keywords:
        ALL_KEYWORDS[kw.lower()] = category


class KeywordExtractor:
    """Extract key terms from job descriptions for ATS resume optimization"""

    def __init__(self):
        self._ai_provider = None

    def extract(self, job_description: str, user_skills: List[str] = None, max_keywords: int = 20) -> List[str]:
        """
        Extract 15-20 key terms from a job description.
        Returns terms that should appear in the resume.
        """
        if not job_description:
            return []

        desc_lower = job_description.lower()

        # Step 1: Find matching tech keywords
        found_keywords = []
        for keyword, category in ALL_KEYWORDS.items():
            # Use word boundary matching for short terms
            if len(keyword) <= 3:
                pattern = r'\b' + re.escape(keyword) + r'\b'
                if re.search(pattern, desc_lower):
                    found_keywords.append((keyword, category))
            else:
                if keyword in desc_lower:
                    found_keywords.append((keyword, category))

        # Step 2: Extract years of experience requirements
        exp_patterns = re.findall(r'(\d+)\+?\s*(?:years?|yrs?)\s*(?:of\s*)?(?:experience|exp)', desc_lower)
        if exp_patterns:
            for years in exp_patterns:
                found_keywords.append((f"{years}+ years experience", 'experience'))

        # Step 3: Extract degree requirements
        degree_patterns = ['bachelor', 'master', 'phd', 'computer science', 'bs', 'ms']
        for deg in degree_patterns:
            if deg in desc_lower:
                found_keywords.append((deg, 'education'))

        # Step 4: Deduplicate and prioritize
        seen = set()
        unique_keywords = []
        for kw, cat in found_keywords:
            kw_normalized = kw.lower().strip()
            if kw_normalized not in seen:
                seen.add(kw_normalized)
                unique_keywords.append(kw)

        # Step 5: If user skills provided, prioritize overlapping ones
        if user_skills:
            user_skills_lower = {s.lower() for s in user_skills}
            overlapping = [kw for kw in unique_keywords if kw.lower() in user_skills_lower]
            non_overlapping = [kw for kw in unique_keywords if kw.lower() not in user_skills_lower]
            unique_keywords = overlapping + non_overlapping

        # Step 6: Limit to max_keywords
        result = unique_keywords[:max_keywords]

        return result

    def extract_with_ai(self, job_description: str, max_keywords: int = 20) -> List[str]:
        """Use AI to extract more nuanced keywords"""
        if not self._ai_provider:
            try:
                from modules.ai_providers import AIProviderManager
                self._ai_provider = AIProviderManager()
            except:
                return self.extract(job_description, max_keywords=max_keywords)

        prompt = f"""Extract the {max_keywords} most important keywords and skills from this job description.
Return ONLY a JSON array of strings, nothing else.
Focus on: technical skills, tools, frameworks, methodologies, and key requirements.

Job Description:
{job_description[:600]}
"""

        response = self._ai_provider.generate(prompt, max_tokens=200, temperature=0.1)
        if response:
            try:
                import json
                if '[' in response:
                    start = response.index('[')
                    end = response.rindex(']') + 1
                    return json.loads(response[start:end])[:max_keywords]
            except:
                pass

        # Fallback to regex extraction
        return self.extract(job_description, max_keywords=max_keywords)

    def get_keyword_categories(self, keywords: List[str]) -> Dict:
        """Group extracted keywords by category"""
        from collections import defaultdict
        categories = defaultdict(list)
        for kw in keywords:
            cat = ALL_KEYWORDS.get(kw.lower(), 'other')
            categories[cat].append(kw)
        return dict(categories)
