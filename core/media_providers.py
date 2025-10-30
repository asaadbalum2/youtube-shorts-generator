"""
Media providers for fetching images/videos from free APIs
Supports Pixabay and Pexels for CC0 stock media
"""
import os
import requests
from typing import Dict, List, Optional
from core.config import Config
import random

class MediaProvider:
    """Base class for media providers"""
    
    def search_images(self, query: str, per_page: int = 10) -> List[Dict]:
        """Search for images"""
        raise NotImplementedError
    
    def search_videos(self, query: str, per_page: int = 10) -> List[Dict]:
        """Search for videos"""
        raise NotImplementedError

class PixabayProvider(MediaProvider):
    """Pixabay API provider - free images and videos"""
    
    def __init__(self):
        self.api_key = os.getenv('PIXABAY_API_KEY', Config.PIXABAY_API_KEY if hasattr(Config, 'PIXABAY_API_KEY') else None)
        self.base_url = "https://pixabay.com/api/"
    
    def search_images(self, query: str, per_page: int = 10) -> List[Dict]:
        """Search for images on Pixabay"""
        if not self.api_key:
            print("⚠️ PIXABAY_API_KEY not configured")
            return []
        
        try:
            params = {
                'key': self.api_key,
                'q': query,
                'image_type': 'photo',
                'orientation': 'vertical',  # For YouTube Shorts (9:16)
                'safesearch': 'true',
                'per_page': per_page
            }
            response = requests.get(f"{self.base_url}", params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            results = []
            for hit in data.get('hits', []):
                results.append({
                    'id': hit.get('id'),
                    'url': hit.get('webformatURL') or hit.get('largeImageURL'),
                    'preview_url': hit.get('previewURL'),
                    'width': hit.get('imageWidth'),
                    'height': hit.get('imageHeight'),
                    'tags': hit.get('tags', ''),
                    'provider': 'pixabay',
                    'type': 'image'  # Explicitly mark as image
                })
            
            print(f"✅ Pixabay: Found {len(results)} images for '{query}'")
            return results
            
        except Exception as e:
            print(f"❌ Pixabay API error: {e}")
            return []
    
    def search_videos(self, query: str, per_page: int = 10) -> List[Dict]:
        """Search for videos on Pixabay"""
        if not self.api_key:
            print("⚠️ PIXABAY_API_KEY not configured")
            return []
        
        try:
            params = {
                'key': self.api_key,
                'q': query,
                'video_type': 'all',
                'safesearch': 'true',
                'per_page': per_page
            }
            response = requests.get(f"{self.base_url}videos/", params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            results = []
            for hit in data.get('hits', []):
                # Get medium size video
                videos = hit.get('videos', {})
                video_url = videos.get('medium', {}).get('url') or videos.get('small', {}).get('url')
                
                if video_url:
                    results.append({
                        'id': hit.get('id'),
                        'url': video_url,
                        'preview_url': hit.get('picture_id'),
                        'duration': hit.get('duration', 0),
                        'tags': hit.get('tags', ''),
                        'provider': 'pixabay',
                        'type': 'video'  # Explicitly mark as video
                    })
            
            print(f"✅ Pixabay: Found {len(results)} videos for '{query}'")
            return results
            
        except Exception as e:
            print(f"❌ Pixabay API error: {e}")
            return []

class PexelsProvider(MediaProvider):
    """Pexels API provider - free images and videos"""
    
    def __init__(self):
        self.api_key = os.getenv('PEXELS_API_KEY', Config.PEXELS_API_KEY if hasattr(Config, 'PEXELS_API_KEY') else None)
        self.base_url = "https://api.pexels.com/v1"
        self.headers = {'Authorization': self.api_key} if self.api_key else {}
    
    def search_images(self, query: str, per_page: int = 10) -> List[Dict]:
        """Search for images on Pexels"""
        if not self.api_key:
            print("⚠️ PEXELS_API_KEY not configured")
            return []
        
        try:
            params = {
                'query': query,
                'orientation': 'portrait',  # For YouTube Shorts
                'per_page': per_page
            }
            response = requests.get(
                f"{self.base_url}/search",
                params=params,
                headers=self.headers,
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            
            results = []
            for photo in data.get('photos', []):
                results.append({
                    'id': photo.get('id'),
                    'url': photo.get('src', {}).get('original') or photo.get('src', {}).get('large') or photo.get('src', {}).get('medium'),  # Use original for highest quality
                    'preview_url': photo.get('src', {}).get('tiny'),
                    'width': photo.get('width'),
                    'height': photo.get('height'),
                    'tags': photo.get('alt', ''),
                    'provider': 'pexels',
                    'type': 'image'  # Explicitly mark as image
                })
            
            print(f"✅ Pexels: Found {len(results)} images for '{query}'")
            return results
            
        except Exception as e:
            print(f"❌ Pexels API error: {e}")
            return []
    
    def search_videos(self, query: str, per_page: int = 10) -> List[Dict]:
        """Search for videos on Pexels"""
        if not self.api_key:
            print("⚠️ PEXELS_API_KEY not configured")
            return []
        
        try:
            params = {
                'query': query,
                'orientation': 'portrait',
                'per_page': per_page
            }
            response = requests.get(
                f"{self.base_url}/videos/search",
                params=params,
                headers=self.headers,
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            
            results = []
            for video in data.get('videos', []):
                video_files = video.get('video_files', [])
                # PRIORITIZE HD quality videos (high resolution)
                video_url = None
                # First try HD (highest quality)
                for vf in video_files:
                    if vf.get('quality') == 'hd' and vf.get('width', 0) >= 720:  # HD = 720p+
                        video_url = vf.get('link')
                        break
                # Then try SD if no HD
                if not video_url:
                    for vf in video_files:
                        if vf.get('quality') == 'sd' and vf.get('width', 0) >= 640:
                            video_url = vf.get('link')
                            break
                # Last resort: any video
                if not video_url and video_files:
                    video_url = video_files[0].get('link')
                
                if video_url:
                    results.append({
                        'id': video.get('id'),
                        'url': video_url,
                        'preview_url': video.get('image'),
                        'duration': video.get('duration', 0),
                        'tags': video.get('tags', []),
                        'provider': 'pexels',
                        'type': 'video',  # Explicitly mark as video
                        'width': next((vf.get('width', 0) for vf in video_files if vf.get('link') == video_url), 0),
                        'height': next((vf.get('height', 0) for vf in video_files if vf.get('link') == video_url), 0)
                    })
            
            print(f"✅ Pexels: Found {len(results)} videos for '{query}'")
            return results
            
        except Exception as e:
            print(f"❌ Pexels API error: {e}")
            return []

class MediaFetcher:
    """Unified media fetcher that tries multiple providers"""
    
    def __init__(self):
        self.providers = []
        
        # Try Pexels first (better video quality)
        pexels_key = os.getenv('PEXELS_API_KEY') or Config.PEXELS_API_KEY
        if pexels_key and pexels_key.strip():
            self.providers.append(PexelsProvider())
            print("✅ Pexels provider initialized")
        else:
            print("ℹ️ PEXELS_API_KEY not found in environment")
        
        # Then Pixabay
        pixabay_key = os.getenv('PIXABAY_API_KEY') or Config.PIXABAY_API_KEY
        if pixabay_key and pixabay_key.strip():
            self.providers.append(PixabayProvider())
            print("✅ Pixabay provider initialized")
        else:
            print("ℹ️ PIXABAY_API_KEY not found in environment")
        
        if not self.providers:
            print("⚠️ CRITICAL: No media providers configured! You'll get (~) color backgrounds only.")
            print("   → Add PEXELS_API_KEY or PIXABAY_API_KEY to Replit Secrets")
        else:
            print(f"✅ {len(self.providers)} media provider(s) ready")
    
    def get_image(self, query: str, prefer_video: bool = False) -> Optional[Dict]:
        """Get a single image/video for a query"""
        if not self.providers:
            return None
        
        # Try video first if preferred
        if prefer_video:
            for provider in self.providers:
                videos = provider.search_videos(query, per_page=5)
                if videos:
                    return random.choice(videos)
        
        # Otherwise try images
        for provider in self.providers:
            images = provider.search_images(query, per_page=10)
            if images:
                return random.choice(images)
        
        return None
    
    def get_images(self, query: str, count: int = 5) -> List[Dict]:
        """Get multiple images for a query"""
        if not self.providers:
            return []
        
        all_images = []
        for provider in self.providers:
            images = provider.search_images(query, per_page=count)
            all_images.extend(images)
        
        # Return unique selection, avoiding duplicates by URL
        seen_urls = set()
        unique_images = []
        for img in all_images:
            if img.get('url') and img['url'] not in seen_urls:
                unique_images.append(img)
                seen_urls.add(img['url'])
                if len(unique_images) >= count:
                    break
        
        return unique_images
