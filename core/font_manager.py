"""
Font Manager - Downloads and manages Google Fonts for video creation
Uses Google Fonts API to get high-quality, modern fonts in TTF format
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
        """Download font from Google Fonts in TTF format"""
        try:
            font_name_url = font_name.replace(" ", "+")
            
            # Request Google Fonts CSS with Windows user agent to get TTF URLs
            css_url = f"https://fonts.googleapis.com/css2?family={font_name_url}:wght@{weight}"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            }
            
            response = requests.get(css_url, timeout=10, headers=headers)
            if response.status_code != 200:
                print(f"⚠️ Failed to fetch font CSS: {response.status_code}")
                return False
            
            css_content = response.text
            
            # Extract TTF URL from CSS
            # Google Fonts provides different formats - we want TTF
            import re
            
            # Pattern: url(https://fonts.gstatic.com/...) format('truetype') or .ttf
            # Look for TTF URLs explicitly
            ttf_patterns = [
                r'url\((https://[^)]+\.ttf)\)',  # Direct .ttf URL
                r"url\((https://fonts\.gstatic\.com/[^)]+)\)\s+format\('truetype'\)",  # TTF with format declaration
            ]
            
            ttf_url = None
            for pattern in ttf_patterns:
                match = re.search(pattern, css_content)
                if match:
                    ttf_url = match.group(1)
                    break
            
            # If no TTF found, try to extract any font URL and convert to TTF
            if not ttf_url:
                # Extract WOFF2 URL and try to get TTF equivalent
                woff2_match = re.search(r'url\((https://[^)]+\.woff2)\)', css_content)
                if woff2_match:
                    woff2_url = woff2_match.group(1)
                    # Google Fonts TTF URLs are usually same path with .ttf extension
                    ttf_url = woff2_url.replace('.woff2', '.ttf')
            
            if not ttf_url:
                print(f"⚠️ No TTF URL found in CSS for {font_name}")
                return False
            
            # Download TTF file
            font_response = requests.get(ttf_url, timeout=30, headers=headers)
            
            if font_response.status_code == 200:
                content = font_response.content
                
                # Verify it's actually a font file (TTF starts with specific bytes)
                if len(content) > 1000 and (content[:4] in [b'\x00\x01\x00\x00', b'OTTO', b'ttcf'] or content[0:2] == b'\x00\x01'):
                    output_path.write_bytes(content)
                    print(f"✅ Downloaded font: {font_name} (TTF, {len(content)} bytes)")
                    return True
                else:
                    # If not valid TTF, it might be WOFF2 - try to download TTF directly
                    # Google Fonts TTF direct URL pattern
                    font_id = font_name.lower().replace(" ", "")
                    direct_ttf_url = f"https://fonts.gstatic.com/s/{font_id}/v{weight}/{font_id}-{weight}.ttf"
                    
                    direct_response = requests.get(direct_ttf_url, timeout=30, headers=headers)
                    if direct_response.status_code == 200 and len(direct_response.content) > 1000:
                        output_path.write_bytes(direct_response.content)
                        print(f"✅ Downloaded font: {font_name} (direct TTF)")
                        return True
                    
                    print(f"⚠️ Downloaded file doesn't appear to be valid TTF")
                    return False
            else:
                print(f"⚠️ Failed to download font file: {font_response.status_code}")
                return False
                
        except Exception as e:
            print(f"⚠️ Error downloading font {font_name}: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _get_system_font(self) -> str:
        """Fallback to system fonts"""
        # Try Windows fonts first
        system_fonts = [
            "C:/Windows/Fonts/arialbd.ttf",      # Arial Bold
            "C:/Windows/Fonts/arial.ttf",      # Arial Regular
            "C:/Windows/Fonts/segoeuib.ttf",    # Segoe UI Bold
            "C:/Windows/Fonts/segoeui.ttf",     # Segoe UI Regular
            "C:/Windows/Fonts/calibrib.ttf",    # Calibri Bold
            "C:/Windows/Fonts/impact.ttf",      # Impact
        ]
        
        # Try Linux/Mac fonts
        if not os.path.exists("C:/Windows"):
            system_fonts = [
                "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
                "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
                "/System/Library/Fonts/Helvetica.ttc",
                "/Library/Fonts/Arial.ttf",
            ]
        
        for font in system_fonts:
            if os.path.exists(font):
                return font
        
        # Ultimate fallback - MoviePy will use default
        return "Arial-Bold"
