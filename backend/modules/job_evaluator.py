"""
10-Dimension Job Scoring Engine
Evaluates each job against 10 weighted dimensions using AI.
Assigns grades A-F with gate-pass criteria (C+ to pass).
"""

import json
import os
from typing import Dict, List, Optional
from datetime import datetime
from database.db_helper import db


class JobEvaluator:
    """10-dimension job scoring engine"""

    DIMENSIONS = [
        'role_match',
        'skills_alignment',
        'seniority_fit',
        'compensation',
        'interview_likelihood',
        'growth_potential',
        'company_reputation',
        'location_fit',
        'tech_stack_match',
        'culture_signals',
    ]

    DIMENSION_WEIGHTS = {
        'role_match': 1.5,
        'skills_alignment': 1.5,
        'seniority_fit': 1.2,
        'compensation': 1.0,
        'interview_likelihood': 1.3,
        'growth_potential': 0.8,
        'company_reputation': 0.8,
        'location_fit': 1.0,
        'tech_stack_match': 1.2,
        'culture_signals': 0.7,
    }

    def __init__(self):
        self._ensure_table()
        self._ai_provider = None

    def _ensure_table(self):
        """Create job_evaluations table if it doesn't exist"""
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS job_evaluations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                job_url TEXT NOT NULL UNIQUE,
                job_title TEXT,
                company TEXT,
                overall_score REAL,
                grade TEXT,
                gate_pass BOOLEAN,
                role_match REAL,
                skills_alignment REAL,
                seniority_fit REAL,
                compensation REAL,
                interview_likelihood REAL,
                growth_potential REAL,
                company_reputation REAL,
                location_fit REAL,
                tech_stack_match REAL,
                culture_signals REAL,
                reasoning TEXT,
                evaluated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        conn.close()

    def _get_ai_provider(self):
        """Lazy-load AI provider"""
        if not self._ai_provider:
            from modules.ai_providers import AIProviderManager
            self._ai_provider = AIProviderManager()
        return self._ai_provider

    def evaluate_job(self, job: Dict) -> Dict:
        """Evaluate a single job on all 10 dimensions"""
        title = job.get('title', '')
        company = job.get('company', '')
        description = job.get('description_snippet', '')
        location = job.get('location', '')
        salary = job.get('salary', '')
        job_url = job.get('job_url', '')

        # Check if already evaluated
        existing = self._get_existing_evaluation(job_url)
        if existing:
            return existing

        # Build AI evaluation prompt
        prompt = self._build_evaluation_prompt(job)

        # Try AI evaluation (let AIProviderManager handle fallbacks)
        ai = self._get_ai_provider()
        ai_response = ai.generate(prompt, max_tokens=800, temperature=0.2)

        if ai_response:
            scores = self._parse_ai_scores(ai_response)
            reasoning = self._extract_reasoning(ai_response)
        else:
            # Fallback: heuristic-based scoring
            scores = self._heuristic_scores(job)
            reasoning = "Evaluated using heuristic scoring (no AI provider available)"

        # Calculate weighted overall score
        overall_score = self._calculate_weighted_score(scores)
        grade = self._score_to_grade(overall_score)
        gate_pass = grade in ('A', 'B', 'C')

        evaluation = {
            'dimensions': scores,
            'overall_score': round(overall_score, 1),
            'grade': grade,
            'gate_pass': gate_pass,
            'reasoning': reasoning,
        }

        # Save to database
        self._save_evaluation(job_url, title, company, scores, overall_score, grade, gate_pass, reasoning)

        # Update dedup tracker
        try:
            from modules.deduplication import JobDeduplicator
            dedup = JobDeduplicator()
            dedup.mark_evaluated(job_url, grade, overall_score)
        except:
            pass

        # Attach evaluation to job dict
        job['evaluation'] = evaluation
        return evaluation

    def evaluate_batch(self, jobs: List[Dict]) -> List[Dict]:
        """Evaluate multiple jobs, return sorted by score descending"""
        print(f"\n[Evaluator] Evaluating {len(jobs)} jobs...")
        for i, job in enumerate(jobs):
            try:
                self.evaluate_job(job)
                grade = job.get('evaluation', {}).get('grade', '?')
                score = job.get('evaluation', {}).get('overall_score', 0)
                print(f"  [{i+1}/{len(jobs)}] {grade} ({score}) - {job.get('title', '')} at {job.get('company', '')}")
            except Exception as e:
                print(f"  [{i+1}/{len(jobs)}] ERROR: {e}")
                job['evaluation'] = {'grade': 'F', 'overall_score': 0, 'gate_pass': False, 'dimensions': {}, 'reasoning': str(e)}

        evaluated = sorted(jobs, key=lambda j: j.get('evaluation', {}).get('overall_score', 0), reverse=True)
        gate_passed = sum(1 for j in evaluated if j.get('evaluation', {}).get('gate_pass', False))
        print(f"[Evaluator] Done: {gate_passed}/{len(evaluated)} passed gate (C+ or above)")
        return evaluated

    def _build_evaluation_prompt(self, job: Dict) -> str:
        """Build the AI prompt for job evaluation"""
        return f"""You are a job evaluation assistant. Score this job posting on 10 dimensions (0-100 each).
Return ONLY valid JSON with this exact structure, no other text:

{{
    "role_match": <0-100>,
    "skills_alignment": <0-100>,
    "seniority_fit": <0-100>,
    "compensation": <0-100>,
    "interview_likelihood": <0-100>,
    "growth_potential": <0-100>,
    "company_reputation": <0-100>,
    "location_fit": <0-100>,
    "tech_stack_match": <0-100>,
    "culture_signals": <0-100>,
    "reasoning": "<1-2 sentence summary>"
}}

Scoring Guide:
- role_match: How well the job title/role matches a software engineering career
- skills_alignment: How many common tech skills (Python, JS, React, AWS, etc.) are required
- seniority_fit: Assume mid-level. Score high if mid/senior, low if intern/entry or VP
- compensation: Score 50 if no salary listed. Higher for competitive ranges
- interview_likelihood: Higher for smaller companies, fewer applicants, Easy Apply
- growth_potential: Opportunity for career growth, learning new tech
- company_reputation: Score based on company name recognition and industry standing
- location_fit: Score 90+ for remote, 70 for hybrid, 50 for on-site
- tech_stack_match: Modern tech stack scores higher (Python, React, Node, AWS, Docker, K8s)
- culture_signals: Positive language about work-life balance, diversity, innovation

JOB POSTING:
Title: {job.get('title', 'N/A')}
Company: {job.get('company', 'N/A')}
Location: {job.get('location', 'N/A')}
Salary: {job.get('salary', 'Not listed')}
Easy Apply: {job.get('easy_apply', False)}
Description: {job.get('description_snippet', 'N/A')[:400]}
"""

    def _parse_ai_scores(self, ai_response: str) -> Dict[str, float]:
        """Parse AI JSON response into dimension scores"""
        try:
            # Extract JSON from response
            json_match = ai_response
            if '{' in ai_response:
                start = ai_response.index('{')
                end = ai_response.rindex('}') + 1
                json_match = ai_response[start:end]

            data = json.loads(json_match)
            scores = {}
            for dim in self.DIMENSIONS:
                val = data.get(dim, 50)
                scores[dim] = max(0, min(100, float(val)))
            return scores
        except (json.JSONDecodeError, ValueError) as e:
            print(f"  [Evaluator] Failed to parse AI response: {e}")
            return {dim: 50.0 for dim in self.DIMENSIONS}

    def _extract_reasoning(self, ai_response: str) -> str:
        """Extract reasoning from AI response"""
        try:
            if '{' in ai_response:
                start = ai_response.index('{')
                end = ai_response.rindex('}') + 1
                data = json.loads(ai_response[start:end])
                return data.get('reasoning', '')
        except:
            pass
        return ''

    def _heuristic_scores(self, job: Dict) -> Dict[str, float]:
        """Fallback heuristic-based scoring when no AI is available"""
        title = (job.get('title', '') or '').lower()
        desc = (job.get('description_snippet', '') or '').lower()
        location = (job.get('location', '') or '').lower()
        company = (job.get('company', '') or '').lower()

        scores = {}

        # Role match
        role_keywords = ['engineer', 'developer', 'software', 'sde', 'programmer']
        scores['role_match'] = 80 if any(k in title for k in role_keywords) else 40

        # Skills alignment
        tech_keywords = ['python', 'javascript', 'react', 'node', 'aws', 'docker', 'kubernetes', 'sql', 'typescript', 'go']
        skill_matches = sum(1 for k in tech_keywords if k in desc)
        scores['skills_alignment'] = min(30 + skill_matches * 10, 100)

        # Seniority
        if any(w in title for w in ['senior', 'sr.', 'lead', 'principal', 'staff']):
            scores['seniority_fit'] = 85
        elif any(w in title for w in ['junior', 'jr.', 'intern', 'entry']):
            scores['seniority_fit'] = 40
        else:
            scores['seniority_fit'] = 70

        # Compensation
        scores['compensation'] = 60 if job.get('salary') else 50

        # Interview likelihood
        scores['interview_likelihood'] = 75 if job.get('easy_apply') else 55

        # Growth potential
        scores['growth_potential'] = 65

        # Company reputation
        known_companies = ['google', 'meta', 'amazon', 'microsoft', 'apple', 'netflix', 'stripe',
                          'anthropic', 'openai', 'vercel', 'cloudflare', 'datadog', 'notion']
        scores['company_reputation'] = 90 if any(c in company for c in known_companies) else 60

        # Location fit
        if 'remote' in location:
            scores['location_fit'] = 90
        elif 'hybrid' in location:
            scores['location_fit'] = 70
        else:
            scores['location_fit'] = 55

        # Tech stack match
        modern_stack = ['react', 'next', 'typescript', 'python', 'fastapi', 'docker', 'aws', 'gcp']
        stack_matches = sum(1 for k in modern_stack if k in desc)
        scores['tech_stack_match'] = min(30 + stack_matches * 12, 100)

        # Culture signals
        culture_words = ['remote', 'flexible', 'balance', 'diversity', 'inclusive', 'growth']
        culture_hits = sum(1 for w in culture_words if w in desc)
        scores['culture_signals'] = min(40 + culture_hits * 12, 100)

        return scores

    def _calculate_weighted_score(self, scores: Dict[str, float]) -> float:
        """Calculate weighted overall score from dimension scores"""
        weighted_sum = 0
        total_weight = 0
        for dim, weight in self.DIMENSION_WEIGHTS.items():
            val = scores.get(dim, 50)
            weighted_sum += val * weight
            total_weight += weight
        return weighted_sum / total_weight if total_weight > 0 else 50

    @staticmethod
    def _score_to_grade(score: float) -> str:
        """Convert numeric score to letter grade"""
        if score >= 85:
            return 'A'
        elif score >= 70:
            return 'B'
        elif score >= 55:
            return 'C'
        elif score >= 40:
            return 'D'
        else:
            return 'F'

    def _save_evaluation(self, job_url, title, company, scores, overall_score, grade, gate_pass, reasoning):
        """Save evaluation to database"""
        conn = db.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO job_evaluations
                (job_url, job_title, company, overall_score, grade, gate_pass,
                 role_match, skills_alignment, seniority_fit, compensation,
                 interview_likelihood, growth_potential, company_reputation,
                 location_fit, tech_stack_match, culture_signals, reasoning, evaluated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                job_url, title, company, overall_score, grade, gate_pass,
                scores.get('role_match', 0), scores.get('skills_alignment', 0),
                scores.get('seniority_fit', 0), scores.get('compensation', 0),
                scores.get('interview_likelihood', 0), scores.get('growth_potential', 0),
                scores.get('company_reputation', 0), scores.get('location_fit', 0),
                scores.get('tech_stack_match', 0), scores.get('culture_signals', 0),
                reasoning, datetime.now().isoformat()
            ))
            conn.commit()
        except Exception as e:
            print(f"  [Evaluator] DB save error: {e}")
        finally:
            conn.close()

    def _get_existing_evaluation(self, job_url: str) -> Optional[Dict]:
        """Check if job was already evaluated"""
        if not job_url:
            return None
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM job_evaluations WHERE job_url = ?', (job_url,))
        row = cursor.fetchone()
        conn.close()

        if row:
            row_dict = dict(row)
            return {
                'dimensions': {dim: row_dict.get(dim, 0) for dim in self.DIMENSIONS},
                'overall_score': row_dict.get('overall_score', 0),
                'grade': row_dict.get('grade', 'F'),
                'gate_pass': bool(row_dict.get('gate_pass', False)),
                'reasoning': row_dict.get('reasoning', ''),
            }
        return None

    def get_all_evaluations(self, min_grade: str = None) -> List[Dict]:
        """Get all evaluations from database, optionally filtered by minimum grade"""
        conn = db.get_connection()
        cursor = conn.cursor()

        if min_grade:
            grade_order = {'A': 5, 'B': 4, 'C': 3, 'D': 2, 'F': 1}
            min_val = grade_order.get(min_grade, 0)
            grades_to_include = [g for g, v in grade_order.items() if v >= min_val]
            placeholders = ','.join('?' * len(grades_to_include))
            cursor.execute(f'SELECT * FROM job_evaluations WHERE grade IN ({placeholders}) ORDER BY overall_score DESC', grades_to_include)
        else:
            cursor.execute('SELECT * FROM job_evaluations ORDER BY overall_score DESC')

        evaluations = []
        for row in cursor.fetchall():
            row_dict = dict(row)
            evaluations.append({
                'job_url': row_dict.get('job_url'),
                'job_title': row_dict.get('job_title'),
                'company': row_dict.get('company'),
                'overall_score': row_dict.get('overall_score'),
                'grade': row_dict.get('grade'),
                'gate_pass': bool(row_dict.get('gate_pass')),
                'dimensions': {dim: row_dict.get(dim, 0) for dim in self.DIMENSIONS},
                'reasoning': row_dict.get('reasoning'),
                'evaluated_at': row_dict.get('evaluated_at'),
            })

        conn.close()
        return evaluations
