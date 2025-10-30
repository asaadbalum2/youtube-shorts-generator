"""
Beautiful Web UI for YouTube Shorts Generator
Accessible from anywhere, shows stats, videos, and manual trigger
"""
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
try:
    from fastapi.templating import Jinja2Templates
except ImportError:
    Jinja2Templates = None
from fastapi.staticfiles import StaticFiles
import sqlite3
from datetime import datetime, date
import json
from core.config import Config
from core.database import Database
import os

app = FastAPI(title="YouTube Shorts Generator Dashboard")

# Templates directory
if Jinja2Templates:
    try:
        templates = Jinja2Templates(directory="web/templates")
    except:
        import os
        os.makedirs("web/templates", exist_ok=True)
        templates = Jinja2Templates(directory="web/templates")
else:
    templates = None

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Main dashboard with enhanced stats"""
    try:
        if not templates:
            return HTMLResponse("<h1>Dashboard</h1><p>Jinja2 templates not available. Install: pip install jinja2</p>")
        
        # Get stats from database using Database class
        db_conn = Database()
        
        # Today's stats
        today = date.today().isoformat()
        today_stats = db_conn.get_daily_stats(today)
        
        if today_stats:
            today_videos_created = today_stats.get('videos_created', 0)
            today_uploaded = today_stats.get('videos_uploaded', 0)
            today_views = today_stats.get('total_views', 0)
            today_likes = today_stats.get('total_likes', 0)
        else:
            today_videos_created = today_uploaded = today_views = today_likes = 0
        
        # Overall stats (all-time)
        overall_stats = db_conn.get_overall_stats()
        
        # Most watched videos
        most_watched_videos = db_conn.get_most_watched_videos(limit=5)
        
        # Most watched topics
        most_watched_topics = db_conn.get_most_watched_topics(limit=5)
        
        # Get quota information
        quota_info = get_quota_info()
        
        # Recent videos (last 20)
        db = sqlite3.connect(Config.DATABASE_PATH)
        cursor = db.cursor()
        try:
            cursor.execute("""
                SELECT video_id, title, topic, youtube_url, created_at, status
                FROM videos
                ORDER BY created_at DESC
                LIMIT 20
            """)
            recent_videos_raw = cursor.fetchall()
        except sqlite3.OperationalError:
            recent_videos_raw = []
        db.close()
        
        # Format recent videos
        recent_videos = []
        for video in recent_videos_raw:
            recent_videos.append({
                'id': video[0] if len(video) > 0 and video[0] else '',
                'title': video[1] if len(video) > 1 and video[1] else 'Untitled',
                'topic': video[2] if len(video) > 2 and video[2] else '',
                'url': video[3] if len(video) > 3 and video[3] else '',
                'created': str(video[4]) if len(video) > 4 and video[4] else '',
                'status': video[5] if len(video) > 5 and video[5] else 'pending'
            })
        
        # Debug logging
        import os
        print(f"DEBUG: Rendering dashboard with {len(recent_videos)} videos")
        print(f"DEBUG: Template exists: {os.path.exists('web/templates/dashboard.html')}")
        
        response = templates.TemplateResponse("dashboard.html", {
            "request": request,
            "today_created": today_videos_created,
            "today_uploaded": today_uploaded,
            "today_views": today_views,
            "today_likes": today_likes,
            "overall_stats": overall_stats,
            "most_watched_videos": most_watched_videos,
            "most_watched_topics": most_watched_topics,
            "recent_videos": recent_videos,
            "videos_per_day": Config.VIDEOS_PER_DAY,
            "quota_info": quota_info
        })
        
        print(f"DEBUG: Template response created successfully")
        return response
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        return HTMLResponse(f"""
            <html><body style="font-family: Arial; padding: 20px;">
                <h1>Dashboard Error</h1>
                <p><strong>Error:</strong> {str(e)}</p>
                <details>
                    <summary>Full traceback (click to expand)</summary>
                    <pre style="background: #f5f5f5; padding: 10px; overflow: auto;">{error_details}</pre>
                </details>
            </body></html>
        """)

@app.post("/api/generate")
async def trigger_generation():
    """API endpoint to trigger video generation - redirects to main app"""
    return JSONResponse({
        "status": "redirect",
        "message": "Use POST /generate on the main app endpoint (not /dashboard/api/generate)"
    })

@app.get("/api/stats")
async def get_stats():
    """Get current statistics"""
    try:
        db_conn = Database()
        overall_stats = db_conn.get_overall_stats()
        today = date.today().isoformat()
        today_stats = db_conn.get_daily_stats(today)
        
        return {
            "today": {
                "created": today_stats.get('videos_created', 0) if today_stats else 0,
                "uploaded": today_stats.get('videos_uploaded', 0) if today_stats else 0,
                "views": today_stats.get('total_views', 0) if today_stats else 0,
                "likes": today_stats.get('total_likes', 0) if today_stats else 0
            },
            "overall": overall_stats
        }
    except Exception as e:
        return {"error": str(e), "today": {"created": 0, "uploaded": 0, "views": 0, "likes": 0}}

@app.post("/api/refresh-token")
async def refresh_token():
    """Manually refresh YouTube token"""
    try:
        from core.token_auto_recovery import regenerate_token_auto, update_config_token
        
        print("🔄 Manual token refresh requested via dashboard...")
        new_token = regenerate_token_auto()
        
        if new_token:
            # Update token in memory
            if update_config_token(new_token):
                return {
                    "status": "success",
                    "message": "Token refreshed successfully! Updated in memory.",
                    "token_preview": f"{new_token[:20]}...{new_token[-10:]}"
                }
            else:
                return {
                    "status": "partial_success",
                    "message": "Token generated but couldn't update in memory. Please restart app.",
                    "token_preview": f"{new_token[:20]}...{new_token[-10:]}"
                }
        else:
            return {
                "status": "error",
                "message": "Failed to generate new token. Check logs for details."
            }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error refreshing token: {str(e)}"
        }

@app.get("/api/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "videos_per_day": Config.VIDEOS_PER_DAY,
        "timestamp": datetime.now().isoformat()
    }

def get_quota_info():
    """Get YouTube API quota information"""
    try:
        # Default quota is 10,000 units per day
        DEFAULT_QUOTA = 10000
        
        # Estimate quota usage based on database operations
        # Each upload attempt uses ~1600 units, each auth refresh uses ~1 unit
        db_conn = Database()
        
        # Count upload attempts (successful and failed)
        db = sqlite3.connect(Config.DATABASE_PATH)
        cursor = db.cursor()
        
        try:
            # Count videos that were attempted to upload
            cursor.execute("""
                SELECT COUNT(*) FROM videos 
                WHERE status IN ('uploaded', 'upload_failed', 'processing')
            """)
            upload_attempts = cursor.fetchone()[0] or 0
            
            # Each upload attempt costs ~1600 units
            # Each authentication refresh costs ~1 unit (we'll estimate 5 per video attempt)
            estimated_used = (upload_attempts * 1600) + (upload_attempts * 5)
            
            # Cap at quota limit
            estimated_used = min(estimated_used, DEFAULT_QUOTA)
            estimated_remaining = max(0, DEFAULT_QUOTA - estimated_used)
            quota_percentage = (estimated_used / DEFAULT_QUOTA) * 100
            
        except sqlite3.OperationalError:
            estimated_used = 0
            estimated_remaining = DEFAULT_QUOTA
            quota_percentage = 0
        finally:
            db.close()
        
        # Check if we have a recent quota error in logs (if possible)
        # This is an estimate - actual quota is only visible in Google Cloud Console
        quota_status = "healthy"
        if quota_percentage > 90:
            quota_status = "critical"
        elif quota_percentage > 70:
            quota_status = "warning"
        
        return {
            "estimated_used": estimated_used,
            "estimated_remaining": estimated_remaining,
            "quota_limit": DEFAULT_QUOTA,
            "percentage_used": round(quota_percentage, 1),
            "status": quota_status,
            "quota_console_url": "https://console.cloud.google.com/apis/api/youtube.googleapis.com/quotas",
            "note": "This is an estimate. Check Google Cloud Console for exact usage."
        }
    except Exception as e:
        return {
            "estimated_used": 0,
            "estimated_remaining": 10000,
            "quota_limit": 10000,
            "percentage_used": 0,
            "status": "unknown",
            "quota_console_url": "https://console.cloud.google.com/apis/api/youtube.googleapis.com/quotas",
            "note": f"Error calculating quota: {str(e)}"
        }
