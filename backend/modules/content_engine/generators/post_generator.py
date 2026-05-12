"""Generate LinkedIn posts from content sources"""
from typing import Dict, List
import json
from backend.core.ai.llm_router import llm_router
from backend.core.ai.prompts.content_prompts import get_prompt, CONTENT_PILLARS

class PostGenerator:
    """Generate LinkedIn posts using AI"""

    def __init__(self):
        self.llm = llm_router

    async def generate_post(
        self,
        source_data: Dict,
        pillar: str = "learning_reflection",
        voice_profile: str = ""
    ) -> Dict:
        """
        Generate a LinkedIn post

        Returns:
            {
                'hooks': [str, str, str],  # 3 hook options
                'body': str,
                'cta': str,
                'hashtags': [str],
                'pillar': str
            }
        """

        # Format source data
        source_text = self._format_source_data(source_data)

        # Get prompt
        prompt = get_prompt(pillar, source_text, voice_profile)

        # Generate with AI
        result = await self.llm.generate(
            prompt,
            purpose="content_generation",
            max_tokens=800,
            prefer_quality=True
        )

        # Parse AI response
        parsed = self._parse_ai_response(result['text'])

        return {
            **parsed,
            'pillar': pillar,
            'ai_provider': result['provider'],
            'ai_cost': result['cost']
        }

    def _format_source_data(self, source_data: Dict) -> str:
        """Format source data for prompt"""
        if source_data.get('type') == 'commit':
            return f"""
Repository: {source_data.get('repo')}
Commit: {source_data.get('message')}
Technologies: {', '.join(source_data.get('tech_tags', []))}
"""

        elif source_data.get('type') == 'pull_request':
            return f"""
Repository: {source_data.get('repo')}
PR Title: {source_data.get('title')}
Description: {source_data.get('body', '')[:300]}
"""

        elif source_data.get('type') == 'manual':
            return source_data.get('raw_content', '')

        else:
            return str(source_data)

    def _parse_ai_response(self, text: str) -> Dict:
        """Parse AI response into structured format"""
        try:
            lines = text.strip().split('\n')

            hooks = []
            body = []
            cta = ""
            hashtags = []

            current_section = None

            for line in lines:
                line = line.strip()

                # Detect sections
                if 'hook' in line.lower() and ('option' in line.lower() or ':' in line):
                    current_section = 'hooks'
                    continue
                elif 'post' in line.lower() and 'body' in line.lower():
                    current_section = 'body'
                    continue
                elif 'cta' in line.lower() or 'question' in line.lower():
                    current_section = 'cta'
                    continue
                elif 'hashtag' in line.lower():
                    current_section = 'hashtags'
                    continue

                # Add to appropriate section
                if not line:
                    continue

                if current_section == 'hooks' and line:
                    # Remove numbering
                    cleaned = line.lstrip('0123456789.-) ')
                    if cleaned:
                        hooks.append(cleaned)

                elif current_section == 'body' and line:
                    body.append(line)

                elif current_section == 'cta' and line:
                    cta = line

                elif current_section == 'hashtags' and line:
                    # Extract hashtags
                    tags = [tag.strip('#').strip() for tag in line.split() if '#' in tag or tag.lower().startswith('hashtag')]
                    hashtags.extend([t for t in tags if t and not t.lower() == 'hashtag'])

            return {
                'hooks': hooks[:3] if hooks else ["Here's something I learned recently...", "I made a mistake this week...", "Quick insight from building..."],
                'body': '\n'.join(body) if body else text,
                'cta': cta if cta else "What's your experience with this?",
                'hashtags': hashtags[:5] if hashtags else ['Tech', 'SoftwareEngineering', 'Learning']
            }

        except:
            # Fallback: return raw text
            return {
                'hooks': [text.split('\n')[0], "Here's what I learned...", "I built something interesting..."],
                'body': text,
                'cta': "What do you think?",
                'hashtags': ['Tech', 'Development']
            }

    def suggest_pillar(self, source_data: Dict) -> str:
        """Suggest best content pillar for source"""
        content = str(source_data).lower()

        if 'bug' in content or 'fix' in content or 'debug' in content:
            return 'debugging_story'

        elif 'build' in content or 'implement' in content or 'create' in content:
            return 'project_breakdown'

        elif 'how' in content or 'guide' in content or 'tutorial' in content:
            return 'how_to'

        elif 'learn' in content or 'realize' in content or 'understand' in content:
            return 'learning_reflection'

        else:
            return 'learning_reflection'  # Default
