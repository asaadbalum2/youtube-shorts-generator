"""
Database management for tracking videos, stats, and trends
"""
import sqlite3
import json
from datetime import datetime
from typing import Optional, Dict, List
from config import Config

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
            INSERT INTO videos (video_id, title, description, topic, trend_score, status, video_file_path disorder
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

