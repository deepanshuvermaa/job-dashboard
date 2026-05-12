"""AI-Powered Personalized LinkedIn Message Generator"""
import openai
from typing import Dict, List
from core.config import settings
from modules.resume_parser import ResumeParser

class AIMessageGenerator:
    """Generate personalized LinkedIn DMs using OpenAI based on resume and job posting"""

    def __init__(self, api_key: str = None):
        self.api_key = api_key or settings.OPENAI_API_KEY
        openai.api_key = self.api_key

        # Parse resume once
        self.resume_parser = ResumeParser()
        self.resume_data = self.resume_parser.resume_data

    def generate_recruiter_message(
        self,
        job_data: Dict,
        recruiter_data: Dict,
        message_type: str = "introduction"
    ) -> str:
        """Generate personalized message to recruiter

        Args:
            job_data: Job information (title, company, description)
            recruiter_data: Recruiter info (name, title)
            message_type: Type of message (introduction, follow_up, referral)

        Returns:
            Personalized LinkedIn message
        """

        # Build context for AI
        job_title = job_data.get('title', 'the position')
        company = job_data.get('company', 'your company')
        job_description = job_data.get('description_snippet', '')

        recruiter_name = recruiter_data.get('name', 'there')
        recruiter_title = recruiter_data.get('title', 'Recruiter')

        candidate_name = self.resume_data.get('name', 'I')

        # Filter and prioritize skills (frontend/backend/cloud focus)
        all_skills = self.resume_data.get('skills', [])
        priority_skills = ['Python', 'JavaScript', 'React', 'Node.js', 'AWS', 'Docker', 'MongoDB', 'SQL', 'Express', 'FastAPI']
        top_skills = [s for s in all_skills if s in priority_skills][:5]

        # If less than 5, add remaining skills
        if len(top_skills) < 5:
            remaining = [s for s in all_skills if s not in top_skills]
            top_skills.extend(remaining[:5-len(top_skills)])

        candidate_skills = ', '.join(top_skills)
        experience_years = self.resume_data.get('experience_years', 1)

        # Create personalized prompt
        if message_type == "introduction":
            prompt = f"""You are a professional LinkedIn message writer. Write a concise, personalized LinkedIn message to a recruiter about a job opportunity.

**Job Details:**
- Position: {job_title}
- Company: {company}
- Job Description: {job_description[:300]}

**Recruiter Details:**
- Name: {recruiter_name}
- Title: {recruiter_title}

**Candidate Details (Me):**
- Name: {candidate_name}
- Skills: {candidate_skills}
- Experience: {experience_years} year{'s' if experience_years > 1 else ''} in software development
- Key Technologies: {candidate_skills}

**Requirements:**
1. Keep it under 150 words (LinkedIn DM best practice)
2. Start with a friendly greeting using recruiter's name
3. Mention specific skills from my resume that match the job
4. Show genuine interest in the role and company
5. Include a clear call-to-action (request for a call or interview)
6. Be professional but warm and authentic
7. Do NOT use overly formal language or clichés
8. Do NOT mention "I hope this message finds you well"
9. Make it feel personal, not templated

Write ONLY the message text, no subject line or extra commentary."""

        elif message_type == "follow_up":
            prompt = f"""Write a brief follow-up message to {recruiter_name} at {company} regarding the {job_title} position.

Key points:
- Reaffirm interest in the role
- Mention my skills: {candidate_skills}
- Ask about next steps
- Keep it under 100 words
- Be polite and professional

Write ONLY the message."""

        elif message_type == "connection_request":
            prompt = f"""Write a LinkedIn connection request note (max 200 characters) to {recruiter_name} ({recruiter_title} at {company}).

Mention:
- Interest in {job_title} role
- My background: {candidate_skills}
- Brief and friendly

Write ONLY the connection note."""

        else:
            prompt = f"""Write a professional LinkedIn message to {recruiter_name} about the {job_title} role at {company}.

My skills: {candidate_skills}. Keep it under 150 words. Write ONLY the message."""

        try:
            # Call OpenAI API
            response = openai.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert LinkedIn communication specialist who writes highly personalized, authentic messages that get responses."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8,
                max_tokens=300
            )

            message = response.choices[0].message.content.strip()

            # Clean up any quotes or extra formatting
            message = message.replace('"', '').replace("'", "").strip()

            print(f"✓ Generated {message_type} message for {recruiter_name}")
            return message

        except Exception as e:
            print(f"Error generating message: {e}")
            # Fallback template
            return self._get_fallback_message(job_title, company, recruiter_name)

    def generate_connection_message(
        self,
        person_data: Dict,
        job_data: Dict
    ) -> str:
        """Generate message for 'People Who Can Help' connections"""

        person_name = person_data.get('name', 'there')
        person_title = person_data.get('title', 'Professional')
        job_title = job_data.get('title')
        company = job_data.get('company')

        candidate_name = self.resume_data.get('name', 'I')
        candidate_skills = ', '.join(self.resume_data.get('skills', [])[:3])

        prompt = f"""Write a friendly LinkedIn connection request message (max 200 characters) to {person_name}, who is a {person_title} at {company}.

Context:
- I'm interested in the {job_title} position at {company}
- My background: {candidate_skills}
- Looking to learn more about the team/role

Make it warm, genuine, and brief. Write ONLY the message."""

        try:
            response = openai.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert at writing brief, authentic LinkedIn connection requests that people actually accept."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=100
            )

            message = response.choices[0].message.content.strip()
            message = message.replace('"', '').strip()

            # Ensure it's under 200 chars (LinkedIn limit)
            if len(message) > 200:
                message = message[:197] + "..."

            return message

        except Exception as e:
            print(f"Error: {e}")
            return f"Hi {person_name}, interested in learning about {job_title} role at {company}. Would love to connect!"

    def _get_fallback_message(self, job_title: str, company: str, recruiter_name: str) -> str:
        """Fallback message if AI fails"""
        candidate_name = self.resume_data.get('name', 'I')
        all_skills = self.resume_data.get('skills', [])
        priority_skills = ['Python', 'JavaScript', 'React', 'Node.js', 'AWS']
        top_skills = [s for s in all_skills if s in priority_skills][:3]
        if len(top_skills) < 3:
            remaining = [s for s in all_skills if s not in top_skills]
            top_skills.extend(remaining[:3-len(top_skills)])
        skills = ', '.join(top_skills)

        return f"""Hi {recruiter_name},

I came across the {job_title} position at {company} and was immediately drawn to it. With my background in {skills}, I believe I could bring significant value to your team.

I'd love to discuss how my experience aligns with what you're looking for. Would you be open to a brief conversation?

Thanks for considering!
{candidate_name}"""

    def generate_bulk_messages(
        self,
        jobs: List[Dict],
        max_messages: int = 10
    ) -> List[Dict]:
        """Generate personalized messages for multiple jobs

        Returns:
            List of {job_id, job_title, recruiter_name, message, dm_link}
        """
        messages = []

        for job in jobs[:max_messages]:
            # Get recruiter info
            recruiter = job.get('recruiter_info', {})
            if not recruiter:
                continue

            message = self.generate_recruiter_message(
                job_data=job,
                recruiter_data=recruiter,
                message_type="introduction"
            )

            messages.append({
                'job_id': job.get('id'),
                'job_title': job.get('title'),
                'company': job.get('company'),
                'recruiter_name': recruiter.get('name'),
                'recruiter_title': recruiter.get('title'),
                'message': message,
                'dm_link': recruiter.get('dm_link'),
                'profile_url': recruiter.get('profile_url')
            })

        return messages


# Test
if __name__ == "__main__":
    generator = AIMessageGenerator()

    test_job = {
        'title': 'Senior React Developer',
        'company': 'Google',
        'description_snippet': 'We are looking for an experienced React developer to join our frontend team. Must have 5+ years experience with React, TypeScript, and modern web technologies.'
    }

    test_recruiter = {
        'name': 'Sarah Johnson',
        'title': 'Senior Technical Recruiter'
    }

    print("Generating personalized message...")
    message = generator.generate_recruiter_message(test_job, test_recruiter)

    print("\n=== GENERATED MESSAGE ===")
    print(message)
    print(f"\nCharacter count: {len(message)}")
