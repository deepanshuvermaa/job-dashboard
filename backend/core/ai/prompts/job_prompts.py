"""Prompts for job application automation"""

JOB_ANSWER_PROMPT = """You are helping fill out a job application question.

USER INFORMATION:
{user_info}

QUESTION:
{question}

QUESTION TYPE: {question_type}

INSTRUCTIONS:
- If numeric: Return ONLY the number
- If yes/no: Return ONLY "Yes" or "No"
- If short answer: 1 sentence maximum
- If detailed: Maximum 350 characters
- Don't repeat the question
- Be concise and natural
- Use the user information provided

Answer:"""

COVER_LETTER_PROMPT = """Write a concise cover letter for this job application.

JOB DETAILS:
Title: {job_title}
Company: {company}
Description: {job_description}

YOUR BACKGROUND:
{user_background}

RECENT PROJECTS:
{recent_projects}

Write a compelling but brief cover letter (200-350 characters) that:
- Shows you understand the role
- Highlights relevant experience
- Mentions one specific project/skill
- Expresses genuine interest

Keep it conversational and authentic. Don't use corporate jargon.

Cover letter:"""

JOB_RELEVANCE_PROMPT = """Analyze if this job is relevant for the candidate.

JOB:
Title: {job_title}
Company: {company}
Location: {location}
Description: {job_description}

CANDIDATE PROFILE:
Skills: {skills}
Experience: {experience}
Preferences: {preferences}

Score the relevance from 0.0 to 1.0 where:
- 0.0-0.3: Not relevant
- 0.4-0.6: Somewhat relevant
- 0.7-0.8: Relevant
- 0.9-1.0: Highly relevant

Consider:
- Skill match
- Experience level match
- Location preference
- Company culture fit

Return only the score as a decimal number (e.g., 0.75)

Score:"""

def get_job_answer_prompt(question: str, question_type: str, user_info: dict):
    """Get prompt for answering job question"""
    user_info_str = "\n".join([f"{k}: {v}" for k, v in user_info.items()])
    return JOB_ANSWER_PROMPT.format(
        user_info=user_info_str,
        question=question,
        question_type=question_type
    )

def get_cover_letter_prompt(job: dict, user_data: dict):
    """Get prompt for cover letter"""
    return COVER_LETTER_PROMPT.format(
        job_title=job.get('title', ''),
        company=job.get('company', ''),
        job_description=job.get('description', '')[:500],  # Truncate
        user_background=user_data.get('background', ''),
        recent_projects=user_data.get('recent_projects', '')
    )

def get_relevance_prompt(job: dict, candidate: dict):
    """Get prompt for relevance scoring"""
    return JOB_RELEVANCE_PROMPT.format(
        job_title=job.get('title', ''),
        company=job.get('company', ''),
        location=job.get('location', ''),
        job_description=job.get('description', '')[:500],
        skills=', '.join(candidate.get('skills', [])),
        experience=candidate.get('experience', ''),
        preferences=candidate.get('preferences', '')
    )
