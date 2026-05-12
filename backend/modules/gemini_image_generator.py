"""Gemini AI Image Generator for LinkedIn Posts"""
import os
import base64
import requests
from pathlib import Path
from typing import Dict, List, Optional
from core.config import settings

class GeminiImageGenerator:
    """Generate images for LinkedIn posts using Google's Gemini Imagen"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or settings.GEMINI_API_KEY
        self.base_url = "https://generativelanguage.googleapis.com/v1beta"
        self.model = "imagen-3.0-generate-001"
        self.output_dir = Path(__file__).parent.parent.parent / "generated_images"
        self.output_dir.mkdir(exist_ok=True)
        
    def generate_post_image(self, post_data: Dict, image_type: str = "code_visualization") -> Optional[str]:
        """Generate image based on post content
        
        Args:
            post_data: Dict containing post content, hashtags, pillar
            image_type: Type of image to generate (code_visualization, infographic, stats, concept)
            
        Returns:
            Path to generated image file or None if failed
        """
        if not self.api_key or self.api_key == "YOUR_GEMINI_API_KEY_HERE":
            print("⚠️  Gemini API key not configured. Skipping image generation.")
            return None
            
        try:
            # Create prompt based on post content and type
            prompt = self._create_image_prompt(post_data, image_type)
            
            # Generate image using Gemini Imagen API
            image_path = self._generate_image(prompt, post_data.get('id', 'unknown'))
            
            return image_path
            
        except Exception as e:
            print(f"Error generating image: {e}")
            return None
    
    def _create_image_prompt(self, post_data: Dict, image_type: str) -> str:
        """Create detailed prompt for image generation"""
        
        content = post_data.get('content', '')
        pillar = post_data.get('pillar', 'general')
        
        if image_type == "code_visualization":
            prompt = f"""Create a modern, professional code snippet visualization for a LinkedIn tech post.
            
Topic: {pillar}
Content summary: {content[:200]}

Style requirements:
- Clean, minimalist design with dark theme
- Syntax-highlighted code snippet relevant to the topic
- Modern IDE-style appearance (VS Code aesthetic)
- Include subtle gradient background (dark blue to purple)
- Professional typography
- No text overlays, just visual code representation
- 16:9 aspect ratio, suitable for LinkedIn
- High contrast for readability on mobile"""

        elif image_type == "infographic":
            prompt = f"""Create a sleek infographic for a LinkedIn tech professional post.
            
Topic: {pillar}
Key points from content: {content[:300]}

Design requirements:
- Modern flat design style
- Tech industry color palette (blues, purples, grays)
- Clean icons and visual elements
- Minimal text, maximum visual impact
- Professional and corporate-friendly
- Data visualization elements if applicable
- 16:9 or 1:1 aspect ratio
- LinkedIn-optimized design"""

        elif image_type == "stats":
            prompt = f"""Create a data visualization dashboard for a tech LinkedIn post.
            
Topic: {pillar}
Context: {content[:200]}

Requirements:
- Modern dashboard aesthetic
- Charts and graphs with tech metrics
- Dark theme with neon accents
- Professional business intelligence style
- Clean typography
- No specific numbers, just visual representation
- Suitable for software engineering audience
- 16:9 aspect ratio"""

        else:  # concept
            prompt = f"""Create an abstract tech concept visualization for LinkedIn.
            
Topic: {pillar}
Theme: {content[:150]}

Style:
- Modern abstract design
- Technology and innovation theme
- Geometric shapes and patterns
- Professional color scheme
- Futuristic but corporate-appropriate
- No text required
- 16:9 aspect ratio
- Eye-catching but professional"""
        
        return prompt
    
    def _generate_image(self, prompt: str, post_id: str) -> Optional[str]:
        """Call Gemini Imagen API to generate image"""
        
        try:
            # Using Gemini's Imagen generation endpoint
            url = f"{self.base_url}/models/{self.model}:generateImage?key={self.api_key}"
            
            payload = {
                "prompt": prompt,
                "number_of_images": 1,
                "aspect_ratio": "16:9",
                "safety_filter_level": "block_few",
                "person_generation": "dont_allow"
            }
            
            headers = {
                "Content-Type": "application/json"
            }
            
            response = requests.post(url, json=payload, headers=headers, timeout=60)
            
            if response.status_code == 200:
                result = response.json()
                
                # Extract base64 image data
                if 'generatedImages' in result and len(result['generatedImages']) > 0:
                    image_data = result['generatedImages'][0]['imageBytes']
                    
                    # Save image
                    filename = f"post_{post_id}_{image_type}.png"
                    filepath = self.output_dir / filename
                    
                    # Decode and save
                    with open(filepath, 'wb') as f:
                        f.write(base64.b64decode(image_data))
                    
                    print(f"✓ Image generated: {filepath}")
                    return str(filepath)
                else:
                    print(f"No image in response: {result}")
                    return None
            else:
                print(f"API error {response.status_code}: {response.text}")
                return None
                
        except Exception as e:
            print(f"Error calling Gemini API: {e}")
            return None
    
    def generate_carousel_images(self, post_data: Dict, num_slides: int = 3) -> List[str]:
        """Generate multiple images for a LinkedIn carousel post"""
        
        images = []
        image_types = ["code_visualization", "infographic", "stats"]
        
        for i, img_type in enumerate(image_types[:num_slides]):
            image_path = self.generate_post_image(post_data, img_type)
            if image_path:
                images.append(image_path)
        
        return images
    
    def cleanup_old_images(self, days: int = 7):
        """Delete images older than specified days"""
        import time
        
        now = time.time()
        cutoff = now - (days * 86400)
        
        for img_file in self.output_dir.glob("*.png"):
            if img_file.stat().st_mtime < cutoff:
                img_file.unlink()
                print(f"Deleted old image: {img_file.name}")


# Usage example
if __name__ == "__main__":
    generator = GeminiImageGenerator()
    
    # Test image generation
    test_post = {
        'id': 'test123',
        'content': 'Exploring React Server Components and their impact on modern web development. Revolutionary architecture for better performance.',
        'pillar': 'Web Development',
        'hashtags': ['#React', '#WebDev', '#ServerComponents']
    }
    
    print("Generating test image...")
    image_path = generator.generate_post_image(test_post, "code_visualization")
    
    if image_path:
        print(f"Success! Image saved to: {image_path}")
    else:
        print("Failed to generate image")
