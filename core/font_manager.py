"""
Font Manager - Downloads and manages Google Fonts for video creation
Uses Google Fonts API to get high-quality, modern fonts in TTF format
"""
import os
import requests
from typing import Optional, List
from pathlib import Path
import json


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
        # Google Fonts API key (public, works without auth)
        self.api_key = "AIzaSyD_HTfk2Jm1QWO7hMZYMDN8FjV5x0q1vWo"
    
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
        """Download font from Google Fonts using API method"""
        try:
            # Method 1: Use Google Fonts API v1 to get font metadata
            api_url = f"https://www.googleapis.com/webfonts/v1/webfonts?key={self.api_key}"
            
            try:
                api_response = requests.get(api_url, timeout=10)
                if api_response.status_code == 200:
                    fonts_data = api_response.json()
                    
                    # Find our font
                    font_info = None
                    for f in fonts_data.get('items', []):
                        if f['family'].lower() == font_name.lower():
                            font_info = f
                            break
                    
                    if font_info:
                        # Map weight to variant name
                        weight_to_variant = {
                            "400": "regular",
                            "600": "600", 
                            "700": "700",
                            "900": "900"
                        }
                        variant = weight_to_variant.get(weight, "regular")
                        
                        # Get TTF file URL from files dictionary
                        files = font_info.get('files', {})
                        
                        # Try different variant names
                        variant_names = [variant, weight, f"{weight}regular", f"{variant}regular"]
                        ttf_url = None
                        
                        for v in variant_names:
                            if v in files:
                                ttf_url = files[v]
                                break
                        
                        # If still no URL, use first available variant
                        if not ttf_url and files:
                            ttf_url = list(files.values())[0]
                        
                        if ttf_url:
                            # Download TTF file
                            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
                            font_response = requests.get(ttf_url, timeout=30, headers=headers)
                            
                            if font_response.status_code == 200:
                                content = font_response.content
                                if len(content) > 1000:
                                    output_path.write_bytes(content)
                                    print(f"✅ Downloaded font: {font_name} (TTF, {len(content)} bytes)")
                                    return True
                                else:
                                    print(f"⚠️ Font file too small: {len(content)} bytes")
            except Exception as api_error:
                print(f"⚠️ API method failed: {api_error}")
            
            # Method 2: Direct download from Google Fonts CDN using standard URL pattern
            # Google Fonts CDN pattern: https://fonts.gstatic.com/s/fontname/vXX/fontfile.ttf
            # We need to construct the URL based on font name
            font_id = font_name.lower().replace(" ", "").replace("-", "")
            
            # Common Google Fonts version patterns
            # Try to download using known patterns
            direct_urls = [
                f"https://fonts.gstatic.com/s/{font_id.lower()}/v18/{font_id.lower()}-{weight}.ttf",
                f"https://fonts.gstatic.com/s/{font_id.lower()}/v19/{font_id.lower()}-{weight}.ttf",
                f"https://fonts.gstatic.com/s/{font_id.lower()}/v20/{font_id.lower()}-{weight}.ttf",
            ]
            
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
            for url in direct_urls:
                try:
                    response = requests.get(url, timeout=15, headers=headers)
                    if response.status_code == 200 and len(response.content) > 1000:
                        # Verify it's a TTF file
                        content = response.content
                        if content[:4] in [b'\x00\x01\x00\x00', b'OTTO', b'ttcf'] or content[:2] == b'\x00\x01':
                            output_path.write_bytes(content)
                            print(f"✅ Downloaded font: {font_name} (direct CDN, {len(content)} bytes)")
                            return True
                except:
                    continue
            
            print(f"⚠️ Could not download {font_name} as TTF - all methods failed")
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
            "C:/Windows/Fonts/arial.ttf",       # Arial Regular
            "C:/Windows/Fonts/segoeuib.ttf",    # Segoe UI Bold
            "C:/Windows/Fonts/segoeui.ttf",     # Segoe UI Regular
            "C:/Windows/Fonts/calibrib.ttf",    # Calibri Bold
            "C:/Windows/Fonts/impact.ttf",       # Impact
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
