"""Prompts for content generation"""

CONTENT_PILLARS = {
    "project_breakdown": {
        "tone": "technical but accessible",
        "prompt": """You are writing a LinkedIn post about a software project.

SOURCE MATERIAL:
{source_data}

VOICE PROFILE:
{voice_profile}

Write a post that:
- Explains what you built (one sentence)
- Shares the key technical decision or challenge
- Includes a small mistake or learning moment
- Ends with a question to engage readers

Structure: Problem → Approach → Result → Learning

Keep it 8-12 lines max. First person. Conversational. No buzzwords like "delve", "leverage", "game-changer".
Don't use hashtags in the post body.

Generate:
1. Three hook options (first line that grabs attention)
2. The full post body
3. One engaging CTA question
4. 3-5 relevant hashtags (separately)
"""
    },

    "debugging_story": {
        "tone": "frustrated → curious → triumphant",
        "prompt": """You are writing a LinkedIn post about debugging an issue.

SOURCE MATERIAL:
{source_data}

VOICE PROFILE:
{voice_profile}

Write a debugging story that:
- Starts with the symptom (what broke)
- Shares the investigation journey
- Reveals the "aha" moment
- States the lesson learned

Tone: Honest and relatable. Share the frustration.

Structure: Bug symptom → Investigation → Aha moment → Takeaway

Keep it 6-10 lines. Conversational. No hashtags in body.

Generate:
1. Three hook options
2. Full post body
3. One reflection question
4. 3-5 hashtags
"""
    },

    "learning_reflection": {
        "tone": "thoughtful and honest",
        "prompt": """You are writing a LinkedIn post about a technical insight or learning.

SOURCE MATERIAL:
{source_data}

VOICE PROFILE:
{voice_profile}

Share a learning that:
- Challenges a common belief or assumption
- Comes from real experience (not theory)
- Is specific and actionable
- Shows vulnerability (what you got wrong)

Structure: What I believed → What I learned → Why it matters

Keep it 7-10 lines. Personal. Authentic.

Generate:
1. Three hook options
2. Full post body
3. One thoughtful CTA
4. 3-5 hashtags
"""
    },

    "how_to": {
        "tone": "teaching, patient",
        "prompt": """You are writing a LinkedIn post teaching something practical.

SOURCE MATERIAL:
{source_data}

VOICE PROFILE:
{voice_profile}

Create a how-to post that:
- Explains why this matters (1 line)
- Gives 3-5 clear steps
- Includes one gotcha or pro tip
- Encourages trying it

Structure: Why → How (steps) → Watch out for → Try it

Keep it 10-15 lines. Actionable. Clear.

Generate:
1. Three hook options
2. Full post with numbered steps
3. Encouraging CTA
4. 3-5 hashtags
"""
    },

    "hot_take": {
        "tone": "opinionated but respectful",
        "prompt": """You are writing a LinkedIn post sharing a strong opinion.

SOURCE MATERIAL:
{source_data}

VOICE PROFILE:
{voice_profile}

Share an opinion that:
- Challenges conventional wisdom
- Is backed by your experience
- Acknowledges other viewpoints
- Invites discussion

Structure: Common belief → My view → Why → Open question

Keep it 5-8 lines. Bold but respectful.

Generate:
1. Three hook options (provocative but professional)
2. Full post body
3. Open-ended question to spark discussion
4. 3-5 hashtags
"""
    }
}

def get_prompt(pillar: str, source_data: str, voice_profile: str = ""):
    """Get prompt template for pillar"""
    if pillar not in CONTENT_PILLARS:
        pillar = "learning_reflection"  # Default

    template = CONTENT_PILLARS[pillar]["prompt"]
    return template.format(source_data=source_data, voice_profile=voice_profile or "N/A")
