"""
Notification system for YouTube Shorts Generator
Handles token expiry warnings, viral video alerts, and quota notifications
"""
import os
import smtplib
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart
from datetime import datetime, timedelta
from typing import Dict, List
from core.config import Config
from core.database import Database

class NotificationManager:
    def __init__(self):
        self.db = Database()
        self.email_enabled = bool(Config.EMAIL_ADDRESS and Config.EMAIL_PASSWORD)
    
    def check_token_expiry(self) -> bool:
        """Check if token needs refresh soon (within 24 hours)"""
        # This is an estimate - refresh tokens typically last 6 months
        # We'll check if we've had recent auth failures
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            # Check for recent auth failures (last 24 hours)
            cursor.execute("""
                SELECT COUNT(*) FROM videos 
                WHERE created_at > datetime('now', '-1 day')
                AND (status = 'upload_failed' OR upload_error LIKE '%token%' OR upload_error LIKE '%401%')
            """)
            
            recent_failures = cursor.fetchone()[0] or 0
            conn.close()
            
            # If we have multiple failures in 24h, token might be expiring
            return recent_failures >= 2
            
        except Exception as e:
            print(f"Error checking token expiry: {e}")
            return False
    
    def check_viral_videos(self, threshold_views: int = 10000) -> List[Dict]:
        """Check for videos that might be going viral"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            # Get videos with high view counts from last 7 days
            cursor.execute("""
                SELECT video_id, title, topic, youtube_url, views, created_at
                FROM videos 
                WHERE status = 'uploaded' 
                AND youtube_url IS NOT NULL
                AND views >= ?
                AND created_at > datetime('now', '-7 days')
                ORDER BY views DESC
            """, (threshold_views,))
            
            viral_videos = []
            for row in cursor.fetchall():
                viral_videos.append({
                    'video_id': row[0],
                    'title': row[1],
                    'topic': row[2],
                    'url': row[3],
                    'views': row[4],
                    'created_at': row[5]
                })
            
            conn.close()
            return viral_videos
            
        except Exception as e:
            print(f"Error checking viral videos: {e}")
            return []
    
    def check_quota_status(self) -> Dict:
        """Check quota status and return warning level"""
        try:
            # Estimate quota usage
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT COUNT(*) FROM videos 
                WHERE status IN ('uploaded', 'upload_failed', 'processing')
            """)
            
            upload_attempts = cursor.fetchone()[0] or 0
            conn.close()
            
            # Each upload costs ~1600 units
            estimated_used = upload_attempts * 1600
            quota_limit = 10000
            percentage = (estimated_used / quota_limit) * 100
            
            status = "healthy"
            if percentage > 90:
                status = "critical"
            elif percentage > 70:
                status = "warning"
            
            return {
                'status': status,
                'percentage': percentage,
                'estimated_used': estimated_used,
                'quota_limit': quota_limit
            }
            
        except Exception as e:
            print(f"Error checking quota: {e}")
            return {'status': 'unknown', 'percentage': 0}
    
    def send_email_notification(self, subject: str, body: str) -> bool:
        """Send email notification"""
        if not self.email_enabled:
            print("Email not configured - skipping notification")
            return False
        
        try:
            msg = MimeMultipart()
            msg['From'] = Config.EMAIL_ADDRESS
            msg['To'] = Config.REPORT_RECIPIENT
            msg['Subject'] = f"YouTube Shorts Generator - {subject}"
            
            msg.attach(MimeText(body, 'html'))
            
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(Config.EMAIL_ADDRESS, Config.EMAIL_PASSWORD)
            server.send_message(msg)
            server.quit()
            
            print(f"✅ Email notification sent: {subject}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to send email: {e}")
            return False
    
    def send_token_warning(self):
        """Send token expiry warning"""
        subject = "Token Refresh Recommended"
        body = """
        <h2>🔑 YouTube Token Refresh Recommended</h2>
        <p>Your YouTube refresh token may be expiring soon. To prevent upload failures:</p>
        <ol>
            <li>Go to your dashboard</li>
            <li>Click "Refresh YouTube Token"</li>
            <li>Follow the authorization process</li>
        </ol>
        <p>This will give you another 6+ months before the next refresh is needed.</p>
        """
        return self.send_email_notification(subject, body)
    
    def send_viral_alert(self, videos: List[Dict]):
        """Send viral video alert"""
        subject = f"🔥 {len(videos)} Video(s) Going Viral!"
        
        body = "<h2>🔥 Viral Video Alert!</h2>"
        for video in videos:
            body += f"""
            <div style="border: 1px solid #ddd; padding: 10px; margin: 10px 0; border-radius: 5px;">
                <h3>{video['title']}</h3>
                <p><strong>Topic:</strong> {video['topic']}</p>
                <p><strong>Views:</strong> {video['views']:,}</p>
                <p><strong>Created:</strong> {video['created_at']}</p>
                <p><a href="{video['url']}" target="_blank">Watch on YouTube →</a></p>
            </div>
            """
        
        return self.send_email_notification(subject, body)
    
    def send_quota_warning(self, quota_info: Dict):
        """Send quota warning"""
        subject = f"⚠️ Quota {quota_info['status'].title()}"
        
        body = f"""
        <h2>⚠️ YouTube API Quota {quota_info['status'].title()}</h2>
        <p>You've used <strong>{quota_info['percentage']:.1f}%</strong> of your daily quota.</p>
        <p><strong>Used:</strong> {quota_info['estimated_used']:,} units</p>
        <p><strong>Limit:</strong> {quota_info['quota_limit']:,} units</p>
        """
        
        if quota_info['status'] == 'critical':
            body += "<p><strong>Action needed:</strong> Wait for daily reset or request quota increase.</p>"
        elif quota_info['status'] == 'warning':
            body += "<p><strong>Monitor:</strong> Consider reducing upload frequency or requesting quota increase.</p>"
        
        return self.send_email_notification(subject, body)
    
    def run_daily_checks(self):
        """Run all daily notification checks"""
        print("🔔 Running daily notification checks...")
        
        # Check token expiry
        if self.check_token_expiry():
            print("⚠️ Token may be expiring soon - sending warning")
            self.send_token_warning()
        
        # Check for viral videos
        viral_videos = self.check_viral_videos()
        if viral_videos:
            print(f"🔥 Found {len(viral_videos)} viral video(s) - sending alert")
            self.send_viral_alert(viral_videos)
        
        # Check quota status
        quota_info = self.check_quota_status()
        if quota_info['status'] in ['warning', 'critical']:
            print(f"⚠️ Quota {quota_info['status']} - sending warning")
            self.send_quota_warning(quota_info)
        
        print("✅ Daily notification checks completed")
