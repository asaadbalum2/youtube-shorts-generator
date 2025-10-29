"""
Error recovery and automatic token refresh system
Ensures autonomous operation even when tokens expire
"""
import logging
import time
from typing import Optional
from config import Config

logger = logging.getLogger(__name__)

class ErrorRecovery:
    """Handles errors and automatic recovery"""
    
    @staticmethod
    def handle_api_error(error: Exception, api_name: str, max_retries: int = 3) -> bool:
        """
        Handle API errors with automatic retry
        
        Returns: True if should retry, False if should skip
        """
        error_str = str(error).lower()
        
        # Authentication errors - need token refresh
        if '401' in error_str or 'unauthorized' in error_str or 'invalid_grant' in error_str:
            logger.warning(f"{api_name} authentication error - token may need refresh")
            return True  # Retry after token refresh
        
        # Rate limit errors - wait and retry
        if 'rate limit' in error_str or '429' in error_str or 'quota' in error_str:
            logger.warning(f"{api_name} rate limit hit - waiting before retry")
            time.sleep(60)  # Wait 1 minute
            return True
        
        # Network errors - retry
        if 'timeout' in error_str or 'connection' in error_str or 'network' in error_str:
            logger.warning(f"{api_name} network error - retrying")
            time.sleep(10)
            return True
        
        # Unknown errors - log and skip
        logger.error(f"{api_name} unknown error: {error}")
        return False
    
    @staticmethod
    def validate_api_keys() -> dict:
        """Validate all API keys are set"""
        missing = []
        
        if not Config.GROQ_API_KEY or Config.GROQ_API_KEY.startswith('your_'):
            missing.append('GROQ_API_KEY')
        
        if not Config.REDDIT_CLIENT_ID or Config.REDDIT_CLIENT_ID.startswith('your_'):
            missing.append('REDDIT credentials')
        
        if not Config.YOUTUBE_REFRESH_TOKEN or Config.YOUTUBE_REFRESH_TOKEN.startswith('your_'):
            missing.append('YOUTUBE_REFRESH_TOKEN')
        
        return {
            'valid': len(missing) == 0,
            'missing': missing
        }

