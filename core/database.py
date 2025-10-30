"""
Database management for tracking videos, stats, and trends
"""
import sqlite3
import json
from datetime import datetime
from typing import Optional, Dict, List
from core.config import Config

class Database:
    def __init__(self, db_path: str = Config.DATABASE_PATH):
        self.db_path = db_path
        self.init_database()
    
    def get_connection(self):
        return sqlite3.connect(self.db_path)
    
    def init_database(self):
        """Initialize database tables"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Videos table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS videos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                video_id TEXT UNIQUE,
                title TEXT,
                description TEXT,
                topic TEXT,
                trend_score REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                uploaded_at TIMESTAMP,
                youtube_url TEXT,
                views INTEGER DEFAULT 0,
                likes INTEGER DEFAULT 0,
                status TEXT DEFAULT 'pending',
                video_file_path TEXT,
                upload_error TEXT,
                retry_count INTEGER DEFAULT 0,
                last_retry_at TIMESTAMP
            )
        """)
        
        # Migration: Add new columns if they don't exist (for existing databases)
        try:
            cursor.execute("ALTER TABLE videos ADD COLUMN video_file_path TEXT")
        except sqlite3.OperationalError:
            pass  # Column already exists
        
        try:
            cursor.execute("ALTER TABLE videos ADD COLUMN upload_error TEXT")
        except sqlite3.OperationalError:
            pass  # Column already exists
        
        try:
            cursor.execute("ALTER TABLE videos ADD COLUMN retry_count INTEGER DEFAULT 0")
        except sqlite3.OperationalError:
            pass  # Column already exists
        
        try:
            cursor.execute("ALTER TABLE videos ADD COLUMN last_retry_at TIMESTAMP")
        except sqlite3.OperationalError:
            pass  # Column already exists
        
        # Trends table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS trends (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                topic TEXT,
                source TEXT,
                score REAL,
                metadata TEXT,
                discovered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                used BOOLEAN DEFAULT 0
            )
        """)
        
        # Daily stats table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS daily_stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date DATE UNIQUE,
                videos_created INTEGER DEFAULT 0,
                videos_uploaded INTEGER DEFAULT 0,
                total_views INTEGER DEFAULT 0,
                total_likes INTEGER DEFAULT 0,
                report_sent BOOLEAN DEFAULT 0
            )
        """)
        
        conn.commit()
        conn.close()
    
    def add_video(self, video_data: Dict) -> int:
        """Add a new video record"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO videos (video_id, title, description, topic, trend_score, status, video_file_path)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            video_data.get('video_id'),
            video_data.get('title'),
            video_data.get('description'),
            video_data.get('topic'),
            video_data.get('trend_score', 0),
            video_data.get('status', 'pending'),
            video_data.get('video_file_path')
        ))
        
        video_db_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return video_db_id
    
    def update_video_upload(self, video_id: str, youtube_url: str):
        """Update video after successful upload"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE videos 
            SET uploaded_at = CURRENT_TIMESTAMP, 
                youtube_url = ?, 
                status = 'uploaded'
            WHERE video_id = ?
        """, (youtube_url, video_id))
        
        conn.commit()
        conn.close()
    
    def add_trend(self, topic: str, source: str, score: float, metadata: Dict = None):
        """Add discovered trend"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        metadata_json = json.dumps(metadata) if metadata else None
        
        cursor.execute("""
            INSERT INTO trends (topic, source, score, metadata)
            VALUES (?, ?, ?, ?)
        """, (topic, source, score, metadata_json))
        
        conn.commit()
        conn.close()
    
    def get_unused_trends(self, limit: int = 10) -> List[Dict]:
        """Get unused trends sorted by score"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, topic, source, score, metadata
            FROM trends
            WHERE used = 0
            ORDER BY score DESC
            LIMIT ?
        """, (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        
        trends = []
        for row in rows:
            trends.append({
                'id': row[0],
                'topic': row[1],
                'source': row[2],
                'score': row[3],
                'metadata': json.loads(row[4]) if row[4] else {}
            })
        
        return trends
    
    def mark_trend_used(self, trend_id: int):
        """Mark a trend as used"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE trends SET used = 1 WHERE id = ?
        """, (trend_id,))
        
        conn.commit()
        conn.close()
    
    def update_daily_stats(self, date: str, **kwargs):
        """Update daily statistics"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO daily_stats (date, videos_created, videos_uploaded, total_views, total_likes)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(date) DO UPDATE SET
                videos_created = videos_created + ?,
                videos_uploaded = videos_uploaded + ?,
                total_views = total_views + ?,
                total_likes = total_likes + ?
        """, (
            date, 
            kwargs.get('videos_created', 0),
            kwargs.get('videos_uploaded', 0),
            kwargs.get('total_views', 0),
            kwargs.get('total_likes', 0),
            kwargs.get('videos_created', 0),
            kwargs.get('videos_uploaded', 0),
            kwargs.get('total_views', 0),
            kwargs.get('total_likes', 0)
        ))
        
        conn.commit()
        conn.close()
    
    def get_daily_stats(self, date: str) -> Optional[Dict]:
        """Get stats for a specific date"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT videos_created, videos_uploaded, total_views, total_likes, report_sent
            FROM daily_stats
            WHERE date = ?
        """, (date,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'videos_created': row[0],
                'videos_uploaded': row[1],
                'total_views': row[2],
                'total_likes': row[3],
                'report_sent': bool(row[4])
            }
        return None
    
    def mark_upload_failed(self, video_id: str, error_message: str):
        """Mark video upload as failed and save error"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE videos 
            SET status = 'upload_failed',
                upload_error = ?,
                retry_count = retry_count + 1,
                last_retry_at = CURRENT_TIMESTAMP
            WHERE video_id = ?
        """, (error_message[:500], video_id))  # Limit error message length
        
        conn.commit()
        conn.close()
    
    def get_failed_uploads(self, max_retries: int = 3) -> List[Dict]:
        """Get videos that failed to upload and need retry"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Get videos that failed or haven't been uploaded yet (have file but no URL)
        cursor.execute("""
            SELECT video_id, title, description, topic, video_file_path, retry_count, upload_error
            FROM videos
            WHERE (status = 'upload_failed' OR (status != 'uploaded' AND youtube_url IS NULL))
                AND retry_count < ?
                AND video_file_path IS NOT NULL
            ORDER BY created_at ASC
        """, (max_retries,))
        
        rows = cursor.fetchall()
        conn.close()
        
        videos = []
        for row in rows:
            videos.append({
                'video_id': row[0],
                'title': row[1],
                'description': row[2],
                'topic': row[3],
                'video_file_path': row[4],
                'retry_count': row[5],
                'upload_error': row[6]
            })
        
        return videos
    
    def update_video_file_path(self, video_id: str, file_path: str):
        """Update video file path (for existing videos)"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE videos 
            SET video_file_path = ?
            WHERE video_id = ?
        """, (file_path, video_id))
        
        conn.commit()
        conn.close()
    
    def get_videos_without_file_path(self) -> List[Dict]:
        """Get videos that don't have file paths set"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT video_id, title, status
            FROM videos
            WHERE (video_file_path IS NULL OR video_file_path = '')
                AND youtube_url IS NULL
                AND status != 'uploaded'
        """)
        
        rows = cursor.fetchall()
        conn.close()
        
        videos = []
        for row in rows:
            videos.append({
                'video_id': row[0],
                'title': row[1],
                'status': row[2]
            })
        
        return videos
    
    def get_most_watched_videos(self, limit: int = 10) -> List[Dict]:
        """Get most watched videos"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT video_id, title, topic, youtube_url, views, likes, created_at
            FROM videos
            WHERE status = 'uploaded' AND youtube_url IS NOT NULL
            ORDER BY views DESC
            LIMIT ?
        """, (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        
        videos = []
        for row in rows:
            videos.append({
                'video_id': row[0],
                'title': row[1],
                'topic': row[2],
                'url': row[3],
                'views': row[4] or 0,
                'likes': row[5] or 0,
                'created_at': row[6]
            })
        
        return videos
    
    def get_most_watched_topics(self, limit: int = 10) -> List[Dict]:
        """Get most watched topics (aggregated by topic)"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                topic,
                COUNT(*) as video_count,
                SUM(COALESCE(views, 0)) as total_views,
                SUM(COALESCE(likes, 0)) as total_likes,
                AVG(COALESCE(views, 0)) as avg_views
            FROM videos
            WHERE status = 'uploaded' AND topic IS NOT NULL AND topic != ''
            GROUP BY topic
            ORDER BY total_views DESC
            LIMIT ?
        """, (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        
        topics = []
        for row in rows:
            topics.append({
                'topic': row[0],
                'video_count': row[1],
                'total_views': row[2] or 0,
                'total_likes': row[3] or 0,
                'avg_views': int(row[4] or 0)
            })
        
        return topics
    
    def get_overall_stats(self) -> Dict:
        """Get overall (all-time) statistics"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                COUNT(*) as total_videos,
                SUM(CASE WHEN status='uploaded' THEN 1 ELSE 0 END) as uploaded_videos,
                SUM(COALESCE(views, 0)) as total_views,
                SUM(COALESCE(likes, 0)) as total_likes,
                AVG(COALESCE(views, 0)) as avg_views
            FROM videos
        """)
        
        row = cursor.fetchone()
        
        if row:
            total_videos, uploaded, total_views, total_likes, avg_views = row
            return {
                'total_videos': total_videos or 0,
                'uploaded_videos': uploaded or 0,
                'total_views': int(total_views or 0),
                'total_likes': int(total_likes or 0),
                'avg_views': int(avg_views or 0),
                'success_rate': round((uploaded or 0) / max(total_videos or 1, 1) * 100, 1)
            }
        
        conn.close()
        return {
            'total_videos': 0,
            'uploaded_videos': 0,
            'total_views': 0,
            'total_likes': 0,
            'avg_views': 0,
            'success_rate': 0
        }

