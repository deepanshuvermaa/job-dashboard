"""
LinkedIn Post Generator - Create authentic, human-sounding posts from question prompts
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI
from typing import List, Dict, Optional
from modules.resume_parser import ResumeParser

# Load environment variables
project_root = Path(__file__).parent.parent.parent
env_path = project_root / '.env'
if env_path.exists():
    load_dotenv(dotenv_path=env_path)

# 30 High-Impact LinkedIn Questions
LINKEDIN_QUESTIONS = [
    "Why should anyone hire you or invest in you? What ROI do you bring consistently?",
    "Where were you 5 years ago? How have you grown from then to now?",
    "What was your most recent failure? What did it teach you that success never could?",
    "What's one belief you have that goes against the norm, but you firmly believe in it?",
    "What's your opinion on AI taking over jobs in your industry?",
    "What are the common mistakes people make in your industry?",
    "What's something you wish you learned earlier in your career?",
    "What's the most underrated skill that has helped you get ahead?",
    "Share a client or customer success story. What changed for them?",
    "What problem does your work solve that rarely gets attention?",
    "What's a myth in your profession you want to debunk?",
    "What is the most valuable advice you've received, and when did it finally make sense?",
    "Share a story about your first big break (or heartbreak) professionally.",
    "What's a decision you took that scared you but changed everything?",
    "What's something in your industry you strongly disagree with?",
    "Name a trend everyone is hyping and your honest take on whether it matters.",
    "What's a small change you made that instantly improved your productivity or effectiveness?",
    "Describe a real and relatable day in your professional life.",
    "What's the most fulfilling part of your work right now?",
    "Where do you see yourself and your industry heading in the next 2-3 years?",
    "What daily habit leads to big results for you over time?",
    "Who is someone that changed your career, and why?",
    "Share a before vs after of your journey, mindset, or skills.",
    "What's a pitch or idea you fought for that turned out to be right?",
    "Share three resources (books, tools, or courses) that helped you grow.",
    "What's something you teach often because it still surprises people?",
    "What does leadership mean to you beyond titles and authority?",
    "How does your personal background or identity shape your professional success?",
    "Share a moment when you wanted to quit but didn't. What kept you going?",
    "What's a message you wish more people in your network truly understood?"
]


class LinkedInPostGenerator:
    def __init__(self):
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found")

        self.openai_client = OpenAI(api_key=api_key)
        self.resume_parser = ResumeParser()
        self.resume_data = self.resume_parser.resume_data

    def generate_post_from_question(
        self,
        question: str,
        user_context: Dict = None,
        tone: str = "conversational",
        length: str = "medium"
    ) -> str:
        """Generate a single LinkedIn post from a question"""

        # Extract resume data
        name = self.resume_data.get('name', 'I')
        skills = ', '.join(self.resume_data.get('skills', [])[:5])
        experience_years = self.resume_data.get('experience_years', 1)
        companies = self.resume_data.get('recent_companies', [])

        # User context (optional additional info)
        achievements = user_context.get('achievements', '') if user_context else ''
        industry = user_context.get('industry', 'software development') if user_context else 'software development'
        personal_notes = user_context.get('notes', '') if user_context else ''

        # Length guide
        length_guide = {
            "short": "150-200 words, 2-3 paragraphs",
            "medium": "200-300 words, 3-4 paragraphs",
            "long": "300-400 words, 4-5 paragraphs"
        }

        # Build comprehensive prompt
        prompt = f"""You are {name}, a professional in {industry}. Write an authentic, human LinkedIn post answering this question:

"{question}"

YOUR BACKGROUND:
- Experience: {experience_years} year{'s' if experience_years > 1 else ''} in software development
- Key skills: {skills}
- Companies: {', '.join(companies[:2]) if companies else 'Various tech companies'}
{f'- Notable achievements: {achievements}' if achievements else ''}
{f'- Additional context: {personal_notes}' if personal_notes else ''}

POST REQUIREMENTS:
1. LENGTH: {length_guide.get(length, 'medium')}

2. STRUCTURE:
   - Hook: Start with a bold, attention-grabbing first line (no questions in the hook)
   - Story/Insight: Share a personal experience, lesson, or perspective
   - Key Takeaway: What can others learn from this?
   - Call to Action: Invite conversation (simple question or statement)

3. TONE: {tone}, conversational, authentic

4. CRITICAL WRITING RULES (MUST FOLLOW):
   - Write like you're talking to a friend over coffee
   - Use simple, everyday English (avoid: "leverage", "utilize", "endeavor", "commenced")
   - NO em dashes (—). Use commas, periods, or "and" instead
   - NO explanatory phrases like "Here's the thing", "Let me tell you", "The truth is"
   - Maximum 2 emojis in the ENTIRE post (use sparingly or not at all)
   - Use short sentences. Mix sentence lengths for rhythm.
   - Start some sentences with "And" or "But" for natural flow
   - Include contractions (I'm, don't, can't, it's)
   - Sound human, not corporate

5. AUTHENTICITY:
   - Be specific (mention actual tools, situations, or feelings)
   - Show vulnerability where relevant
   - Don't oversell or sound promotional
   - Use "I" statements, not "we" or "you should"

6. CALL TO ACTION OPTIONS:
   - "What would you do differently?"
   - "Have you experienced this too?"
   - "What's your version of this story?"
   - "Thoughts?"
   - Or end with a reflection, no question needed

Write ONLY the post content. No meta-commentary, no subject line, no hashtags at the end."""

        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert at writing authentic, human-sounding LinkedIn posts. You write like a real person sharing experiences, not like a marketer or AI. You avoid corporate jargon and write conversationally."
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8,  # Higher temperature for more human variation
                max_tokens=500
            )

            post_content = response.choices[0].message.content.strip()

            # Post-processing: Remove any remaining issues
            post_content = post_content.replace('—', ',')  # Replace em dashes
            post_content = post_content.replace('–', ',')  # Replace en dashes

            return post_content

        except Exception as e:
            print(f"Error generating post: {e}")
            return f"Could not generate post from question: {question[:50]}..."

    def generate_bulk_posts(
        self,
        num_posts: int = 50,
        user_context: Dict = None,
        tone: str = "conversational",
        length: str = "medium",
        selected_questions: List[int] = None
    ) -> List[Dict]:
        """Generate multiple posts from the question bank"""

        posts = []

        # If specific questions selected, use those; otherwise use all and repeat if needed
        if selected_questions:
            questions_to_use = [LINKEDIN_QUESTIONS[i] for i in selected_questions if i < len(LINKEDIN_QUESTIONS)]
        else:
            questions_to_use = LINKEDIN_QUESTIONS.copy()

        # If we need more than available questions, cycle through them with variations
        questions_cycle = []
        while len(questions_cycle) < num_posts:
            questions_cycle.extend(questions_to_use)

        questions_cycle = questions_cycle[:num_posts]

        print(f"Generating {num_posts} LinkedIn posts...")

        for i, question in enumerate(questions_cycle):
            print(f"Generating post {i+1}/{num_posts}: {question[:60]}...")

            # Vary tone slightly for diversity
            tones = ["conversational", "professional", "casual", "inspirational"]
            post_tone = tone if i % 4 == 0 else tones[i % 4]

            post_content = self.generate_post_from_question(
                question=question,
                user_context=user_context,
                tone=post_tone,
                length=length
            )

            posts.append({
                'question': question,
                'content': post_content,
                'tone': post_tone,
                'length': length,
                'number': i + 1
            })

        print(f"✓ Generated {len(posts)} posts successfully")
        return posts

    def get_question_categories(self) -> Dict[str, List[int]]:
        """Organize questions by category for easier selection"""
        categories = {
            "Personal Growth & Journey": [1, 2, 6, 7, 12, 13, 22, 23, 28],
            "Industry Insights & Opinions": [4, 5, 10, 11, 14, 15, 16, 19],
            "Skills & Productivity": [7, 8, 17, 20, 25],
            "Stories & Experiences": [3, 9, 13, 18, 21, 24, 29],
            "Leadership & Vision": [0, 19, 26, 27, 30],
            "Common Mistakes & Myths": [6, 11, 15]
        }
        return categories


# Test function
if __name__ == "__main__":
    generator = LinkedInPostGenerator()

    # Sample user context
    user_context = {
        'industry': 'Full Stack Development',
        'achievements': 'Built SaaS platforms, scaled to 100+ users, improved ROI by 60%',
        'notes': 'Recent CS graduate, passionate about automation and AI'
    }

    # Generate a single test post
    print("=== TEST: Single Post Generation ===\n")
    test_post = generator.generate_post_from_question(
        question=LINKEDIN_QUESTIONS[0],
        user_context=user_context,
        tone="conversational",
        length="medium"
    )

    print(test_post)
    print(f"\n\nWord count: {len(test_post.split())}")
    print(f"Character count: {len(test_post)}")
