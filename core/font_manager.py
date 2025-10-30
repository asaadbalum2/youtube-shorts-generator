"""
Font Manager - Downloads and manages Google Fonts for video creation
Uses GitHub CDN directly (most reliable) + Google Fonts API as fallback
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
    
    # GitHub raw URLs for Google Fonts (RELIABLE, always works)
    FONT_GITHUB_MAP = {
        "bebas neue": {
            "400": "https://github.com/google/fonts/raw/main/ofl/bebasneue/BebasNeue-Regular.ttf",
            "700": "https://github.com/google/fonts/raw/main/ofl/bebasneue/BebasNeue-Regular.ttf",  # Bebas Neue only has one weight
            "900": "https://github.com/google/fonts/raw/main/ofl/bebasneue/BebasNeue-Regular.ttf",
        },
        "montserrat": {
            "400": "https://github.com/google/fonts/raw/main/ofl/montserrat/Montserrat-Regular.ttf",
            "700": "https://github.com/google/fonts/raw/main/ofl/montserrat/Montserrat-Bold.ttf",
            "900": "https://github.com/google/fonts/raw/main/ofl/montserrat/Montserrat-Black.ttf",
        },
        "poppins": {
            "400": "https://github.com/google/fonts/raw/main/ofl/poppins/Poppins-Regular.ttf",
            "700": "https://github.com/google/fonts/raw/main/ofl/poppins/Poppins-Bold.ttf",
            "900": "https://github.com/google/fonts/raw/main/ofl/poppins/Poppins-Black.ttf",
        },
        "roboto": {
            "400": "https://github.com/google/fonts/raw/main/apache/roboto/Roboto-Regular.ttf",
            "700": "https://github.com/google/fonts/raw/main/apache/roboto/Roboto-Bold.ttf",
            "900": "https://github.com/google/fonts/raw/main/apache/roboto/Roboto-Black.ttf",
        },
        "inter": {
            "400": "https://github.com/google/fonts/raw/main/ofl/inter/Inter-Regular.ttf",
            "700": "https://github.com/google/fonts/raw/main/ofl/inter/Inter-Bold.ttf",
            "900": "https://github.com/google/fonts/raw/main/ofl/inter/Inter-Black.ttf",
        },
    }
    
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
        """Download font from GitHub (most reliable) or Google Fonts"""
        try:
            font_key = font_name.lower()
            
            # Method 1: GitHub Raw URLs (MOST RELIABLE - always works)
            if font_key in self.FONT_GITHUB_MAP:
                weight_map = self.FONT_GITHUB_MAP[font_key]
                # Use exact weight if available, otherwise use closest
                url = weight_map.get(weight, weight_map.get("700", weight_map.get("400")))
                
                if url:
                    try:
                        headers = {'User-Agent': 'Mozilla/5.0'}
                        response = requests.get(url, timeout=30, headers=headers, allow_redirects=True)
                        
                        if response.status_code == 200:
                            content = response.content
                            if len(content) > 1000:
                                output_path.write_bytes(content)
                                print(f"✅ Downloaded font: {font_name} from GitHub (TTF, {len(content)} bytes)")
                                return True
                            else:
                                print(f"⚠️ GitHub font too small: {len(content)} bytes")
                    except Exception as gh_error:
                        print(f"⚠️ GitHub download failed: {gh_error}")
            
            # Method 2: Google Fonts API v1
            try:
                api_key = "AIzaSyD_HTfk2Jm1QWO7hMZYMDN8FjV5x0q1vWo"
                api_url = f"https://www.googleapis.com/webfonts/v1/webfonts?key={api_key}"
                
                api_response = requests.get(api_url, timeout=10)
                if api_response.status_code == 200:
                    fonts_data = api_response.json()
                    
                    font_info = None
                    for f in fonts_data.get('items', []):
                        if f['family'].lower() == font_name.lower():
                            font_info = f
                            break
                    
                    if font_info:
                        weight_to_variant = {"400": "regular", "600": "600", "700": "700", "900": "900"}
                        variant = weight_to_variant.get(weight, "regular")
                        
                        files = font_info.get('files', {})
                        variant_names = [variant, weight, f"{weight}regular", f"{variant}regular"]
                        ttf_url = None
                        
                        for v in variant_names:
                            if v in files:
                                ttf_url = files[v]
                                break
                        
                        if not ttf_url and files:
                            ttf_url = list(files.values())[0]
                        
                        if ttf_url:
                            headers = {'User-Agent': 'Mozilla/5.0'}
                            font_response = requests.get(ttf_url, timeout=30, headers=headers)
                            
                            if font_response.status_code == 200 and len(font_response.content) > 1000:
                                output_path.write_bytes(font_response.content)
                                print(f"✅ Downloaded font: {font_name} from Google Fonts API (TTF)")
                                return True
            except Exception as api_error:
                print(f"⚠️ API method failed: {api_error}")
            
            # Method 3: Try GitHub generic path (for fonts not in our map)
            font_id = font_name.lower().replace(" ", "")
            github_urls = [
                f"https://github.com/google/fonts/raw/main/ofl/{font_id}/{font_id.capitalize()}-{weight}.ttf",
                f"https://github.com/google/fonts/raw/main/ofl/{font_id}/{font_name.replace(' ', '')}-{weight}.ttf",
                f"https://github.com/google/fonts/raw/main/ofl/{font_id}/{font_name.replace(' ', '')}-Regular.ttf",
            ]
            
            for url in github_urls:
                try:
                    headers = {'User-Agent': 'Mozilla/5.0'}
                    response = requests.get(url, timeout=15, headers=headers, allow_redirects=True)
                    if response.status_code == 200 and len(response.content) > 1000:
                        output_path.write_bytes(response.content)
                        print(f"✅ Downloaded font: {font_name} from GitHub (generic, {len(response.content)} bytes)")
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
