"""
AI Image Generation using Hugging Face (Free)
Generate images based on video topic/script
"""
import os
from typing import Optional, Dict
from core.config import Config

try:
    from huggingface_hub import InferenceClient
    HF_AVAILABLE = True
except ImportError:
    HF_AVAILABLE = False
    print("⚠️ huggingface_hub not installed. Run: pip install huggingface_hub")

class AIImageGenerator:
    """Generate images using Hugging Face Stable Diffusion"""
    
    def __init__(self):
        self.api_key = os.getenv('HUGGINGFACE_API_KEY', '')
        if not self.api_key:
            print("⚠️ HUGGINGFACE_API_KEY not configured")
            self.client = None
        elif HF_AVAILABLE:
            self.client = InferenceClient(token=self.api_key)
            print("✅ Hugging Face client initialized")
        else:
            self.client = None
    
    def generate_image(self, prompt: str, style: str = "realistic") -> Optional[str]:
        """
        Generate image from text prompt
        Returns path to generated image
        """
        if not self.client or not HF_AVAILABLE:
            return None
        
        try:
            # Enhance prompt based on style
            enhanced_prompt = self._enhance_prompt(prompt, style)
            
            # Use free Stable Diffusion model
            image = self.client.text_to_image(
                prompt=enhanced_prompt,
                model="runwayml/stable-diffusion-v1-5"
            )
            
            # Save image
            import os
            image_path = os.path.join(Config.TEMP_DIR, f"ai_image_{hash(prompt) % 10000}.png")
            os.makedirs(Config.TEMP_DIR, exist_ok=True)
            image.save(image_path)
            
            print(f"✅ AI image generated: {image_path}")
            return image_path
            
        except Exception as e:
            print(f"⚠️ AI image generation error: {e}")
            return None
    
    def _enhance_prompt(self, prompt: str, style: str) -> str:
        """Enhance prompt with style keywords"""
        style_keywords = {
            "realistic": "high quality, photorealistic, 8k, detailed",
            "cinematic": "cinematic lighting, dramatic, epic, professional photography",
            "minimalist": "minimal, simple, clean, modern design",
            "vibrant": "vibrant colors, bold, eye-catching, dynamic"
        }
        
        keywords = style_keywords.get(style, style_keywords["realistic"])
        return f"{prompt}, {keywords}, vertical portrait 9:16 aspect ratio"

