"""
Beautiful Web UI for YouTube Shorts Generator
Accessible from anywhere, shows stats, videos, and manual trigger
"""
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
try:
    from fastapi.templating import Jinja2Templates
except ImportError:
    # Fallback if jinja2 not installed
    Jinja2Templates = None
from fastapi.staticfiles import StaticFiles
import sqlite3
from datetime import datetime, date
import json
from config import Config

app = FastAPI(title="YouTube Shorts Generator Dashboard")

# Templates directory
if Jinja2Templates:
    try:
        templates = Jinja2Templates(directory="templates")
    except:
        import os
        os.makedirs("templates", exist_ok=True)
        templates = Jinja2Templates(directory="templates")
else:
    templates = None

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Main dashboard"""
    try:
        if not templates:
            return HTMLResponse("<h1>Dashboard</h1><p>Jinja2 templates not available. Install: pip install jinja2</p>")
        
        # Get stats from database
        db = sqlite3.connect(Config.DATABASE_PATH)
        cursor = db.cursor()
    
    # Today's stats
    today = date.today().isoformat()
    cursor.execute("""
        SELECT videos_created, videos_uploaded, total_views, total_likes
        FROM daily_stats WHERE date = ?
    """, (today,))
    today_stats = cursor.fetchone()
    
    if today_stats:
        today_videos_created, today_uploaded, today_views, today_likes = today_stats
    else:
        today_videos_created = today_uploaded = today_views = today_likes = 0
    
    # Recent videos
    cursor.execute("""
        SELECT video_id, title, topic, youtube_url, created_at, status
        FROM videos
        ORDER BY created_at DESC
        LIMIT 20
    """)
    recent_videos = cursor.fetchall()
    
    # Total stats
    cursor.execute("""
        SELECT 
            COUNT(*) as total,
            SUM(CASE WHEN status='uploaded' THEN 1 ELSE 0 END) as uploaded,
            SUM(views) as total_views,
            SUM(likes) as total_likes
        FROM videos
    """)
    total_stats = cursor.fetchone()
    
    db.close()
    
    # Format videos
    videos = []
    for video in recent_videos:
        videos.append({
            'id': video[0],
            'title': video[1],
            'topic': video[2],
            'url': video[3],
            'created': video[4],
            'status': video[5]
        })
    
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "today_created": today_videos_created,
        "today_uploaded": today_uploaded,
        "today_views": today_views,
        "today_likes": today_likes,
        "total_videos": total_stats[0] or 0,
        "total_uploaded": total_stats[1] or 0,
        "total_views": total_stats[2] or 0,
        "total_likes": total_stats[3] or 0,
        "recent_videos": videos,
        "videos_per_day": Config.VIDEOS_PER_DAY
    })
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
    """API endpoint to trigger video generation"""
    # This will be called by the main app
    # We'll use a simple file-based trigger
    try:
        with open("trigger_generation.flag", "w") as f:
            f.write(str(datetime.now()))
        return {"status": "success", "message": "Generation triggered - check logs"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/api/stats")
async def get_stats():
    """Get current statistics"""
    db = sqlite3.connect(Config.DATABASE_PATH)
    cursor = db.cursor()
    
    today = date.today().isoformat()
    cursor.execute("""
        SELECT videos_created, videos_uploaded, total_views, total_likes
        FROM daily_stats WHERE date = ?
    """, (today,))
    stats = cursor.fetchone()
    
    db.close()
    
    if stats:
        return {
            "today": {
                "created": stats[0],
                "uploaded": stats[1],
                "views": stats[2],
                "likes": stats[3]
            }
        }
    return {"today": {"created": 0, "uploaded": 0, "views": 0, "likes": 0}}

@app.get("/api/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "videos_per_day": Config.VIDEOS_PER_DAY,
        "timestamp": datetime.now().isoformat()
    }

