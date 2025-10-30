"""
Font Manager - Downloads and manages Google Fonts for video creation
Uses Google Fonts API to get high-quality, modern fonts
"""
import os
import requests
from typing import Optional, List
from pathlib import Path


class FontManager:
    """Manages font downloads and selection for YouTube Shorts"""
    
    # Popular YouTube Shorts-style fonts from Google Fonts
    YOUTUBE_SHORTS_FONTS = [
        "Bebas Neue",      # Bold, modern, eye-catching
        "Montserrat",      # Clean, professional
        "Poppins",         # Modern, friendly
        "Roboto",          # Google's modern font
        "Inter",           # Clean, readable
        "Open Sans",       # Professional, versatile
        "Nunito",          # Rounded, friendly
        "Raleway",         # Elegant, modern
    ]
    
    def __init__(self):
        self.fonts_dir = Path("./assets/fonts")
        self.fonts_dir.mkdir(parents=True, exist_ok=True)
        self.api_base = "https://www.googleapis.com/webfonts/v1/webfonts"
    
    def get_font_path(self, font_name: str = None, weight: str = "700") -> str:
        """
        Get path to font file, downloading if necessary
        weight: "400" (regular), "600" (semi-bold), "700" (bold), "900" (black)
        """
        if not font_name:
            font_name = "Bebas Neue"  # Default: bold, YouTube Shorts style
        
        # Clean font name for filename
        font_filename = font_name.replace(" ", "-").lower()
        font_path = self.fonts_dir / f"{font_filename}-{weight}.ttf"
        
        # If font doesn't exist, download it
        if not font_path.exists():
            print(f"📥 Downloading font: {font_name} (weight: {weight})")
            downloaded = self._download_google_font(font_name, weight, font_path)
            if not downloaded:
                # Fallback to system fonts
                return self._get_system_font()
        
        return str(font_path) if font_path.exists() else self._get_system_font()
    
    def _download_google_font(self, font_name: str, weight: str, output_path: Path) -> bool:
        """Download font from Google Fonts"""
        try:
            # Google Fonts CDN URL
            font_name_url = font_name.replace(" ", "+")
            url = f"https://fonts.googleapis.com/css2?family={font_name_url}:wght@{weight}"
            
            # Get CSS file to find font URL
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                css_content = response.text
                # Extract font URL from CSS
                import re
                font_url_match = re.search(r'url\((https://[^)]+\.woff2?)\)', css_content)
                if font_url_match:
                    font_url = font_url_match.group(1)
                    # Download font file
                    font_response = requests.get(font_url, timeout=30)
                    if font_response.status_code == 200:
                        # Convert WOFF2 to TTF if needed, or save as WOFF2
                        # MoviePy can use TTF, so try to convert or use directly
                        if font_url.endswith('.woff2'):
                            # For now, save as woff2 and let system handle it
                            # In future, could convert using fonttools
                            output_path = output_path.with_suffix('.woff2')
                        
                        output_path.write_bytes(font_response.content)
                        print(f"✅ Downloaded font: {font_name}")
                        return True
        except Exception as e:
            print(f"⚠️ Error downloading font {font_name}: {e}")
        
        return False
    
    def _get_system_font(self) -> str:
        """Fallback to system fonts"""
        system_fonts = [
            "C:/Windows/Fonts/arialbd.ttf",
            "C:/Windows/Fonts/segoeuib.ttf",
            "C:/Windows/Fonts/calibrib.ttf",
        ]
        
        for font in system_fonts:
            if os.path.exists(font):
                return font
        
        return "Arial-Bold"  # MoviePy fallback

