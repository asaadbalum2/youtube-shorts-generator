"""
Quota management system for YouTube API
Optimizes quota usage and prevents overconsumption
"""
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from core.config import Config
from core.database import Database

class QuotaManager:
    def __init__(self):
        self.db = Database()
        self.daily_quota_limit = 10000  # Default YouTube API quota
        self.upload_cost = 1600  # Cost per upload attempt
        self.auth_cost = 1  # Cost per auth refresh
        
    def get_quota_usage_estimate(self) -> Dict:
        """Get estimated quota usage for today"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            # Count upload attempts today
            cursor.execute("""
                SELECT COUNT(*) FROM videos 
                WHERE DATE(created_at) = DATE('now')
                AND status IN ('uploaded', 'upload_failed', 'processing')
            """)
            uploads_today = cursor.fetchone()[0] or 0
            
            # Estimate auth refreshes (roughly 2 per upload attempt)
            auth_refreshes = uploads_today * 2
            
            # Calculate total usage
            total_used = (uploads_today * self.upload_cost) + (auth_refreshes * self.auth_cost)
            remaining = max(0, self.daily_quota_limit - total_used)
            percentage = (total_used / self.daily_quota_limit) * 100
            
            conn.close()
            
            return {
                'used': total_used,
                'remaining': remaining,
                'limit': self.daily_quota_limit,
                'percentage': round(percentage, 1),
                'uploads_today': uploads_today,
                'status': self._get_status(percentage)
            }
            
        except Exception as e:
            print(f"Error calculating quota usage: {e}")
            return {
                'used': 0,
                'remaining': self.daily_quota_limit,
                'limit': self.daily_quota_limit,
                'percentage': 0,
                'uploads_today': 0,
                'status': 'unknown'
            }
    
    def _get_status(self, percentage: float) -> str:
        """Get quota status based on percentage"""
        if percentage >= 95:
            return 'critical'
        elif percentage >= 80:
            return 'warning'
        elif percentage >= 60:
            return 'moderate'
        else:
            return 'healthy'
    
    def can_upload(self) -> bool:
        """Check if we can safely upload without exceeding quota"""
        usage = self.get_quota_usage_estimate()
        return usage['remaining'] >= self.upload_cost
    
    def get_safe_upload_count(self) -> int:
        """Get number of safe uploads remaining today"""
        usage = self.get_quota_usage_estimate()
        return max(0, usage['remaining'] // self.upload_cost)
    
    def should_pause_uploads(self) -> bool:
        """Check if we should pause uploads to preserve quota"""
        usage = self.get_quota_usage_estimate()
        return usage['status'] in ['warning', 'critical']
    
    def get_quota_recommendations(self) -> List[str]:
        """Get recommendations for quota management"""
        usage = self.get_quota_usage_estimate()
        recommendations = []
        
        if usage['status'] == 'critical':
            recommendations.extend([
                "🚨 CRITICAL: Pause all uploads immediately",
                "Wait for daily quota reset (midnight Pacific Time)",
                "Consider requesting quota increase in Google Cloud Console",
                "Review failed uploads to reduce retry attempts"
            ])
        elif usage['status'] == 'warning':
            recommendations.extend([
                "⚠️ WARNING: Reduce upload frequency",
                f"Only {usage['remaining']} units remaining",
                "Consider pausing until tomorrow",
                "Monitor quota usage closely"
            ])
        elif usage['status'] == 'moderate':
            recommendations.extend([
                "📊 MODERATE: Monitor usage",
                f"Safe to upload {self.get_safe_upload_count()} more videos",
                "Consider reducing upload frequency if needed"
            ])
        else:
            recommendations.extend([
                "✅ HEALTHY: Normal operation",
                f"Safe to upload {self.get_safe_upload_count()} more videos",
                "Continue with scheduled uploads"
            ])
        
        return recommendations
    
    def log_quota_usage(self, operation: str, cost: int):
        """Log quota usage for tracking"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            # Create quota_logs table if it doesn't exist
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS quota_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    operation TEXT NOT NULL,
                    cost INTEGER NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    remaining_estimate INTEGER
                )
            """)
            
            # Get current usage estimate
            usage = self.get_quota_usage_estimate()
            
            # Log the operation
            cursor.execute("""
                INSERT INTO quota_logs (operation, cost, remaining_estimate)
                VALUES (?, ?, ?)
            """, (operation, cost, usage['remaining']))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"Error logging quota usage: {e}")
    
    def get_quota_history(self, days: int = 7) -> List[Dict]:
        """Get quota usage history for the past N days"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 
                    DATE(timestamp) as date,
                    SUM(cost) as total_cost,
                    COUNT(*) as operations
                FROM quota_logs 
                WHERE timestamp >= datetime('now', '-{} days')
                GROUP BY DATE(timestamp)
                ORDER BY date DESC
            """.format(days))
            
            history = []
            for row in cursor.fetchall():
                history.append({
                    'date': row[0],
                    'total_cost': row[1],
                    'operations': row[2]
                })
            
            conn.close()
            return history
            
        except Exception as e:
            print(f"Error getting quota history: {e}")
            return []
    
    def send_history_email(self, days: int = 7) -> bool:
        """Send quota history via email before cleanup"""
        try:
            from core.notifications import NotificationManager
            notifications = NotificationManager()
            
            history = self.get_quota_history(days)
            
            if not history:
                return True  # No history to send
            
            subject = f"Quota History Report ({days} days)"
            body = f"""
            <h2>📊 YouTube API Quota History Report</h2>
            <p>This data will be cleaned up from the database. Here's the {days}-day history:</p>
            
            <table style="border-collapse: collapse; width: 100%; margin: 20px 0;">
                <tr style="background: #f5f5f5;">
                    <th style="border: 1px solid #ddd; padding: 8px;">Date</th>
                    <th style="border: 1px solid #ddd; padding: 8px;">Total Cost</th>
                    <th style="border: 1px solid #ddd; padding: 8px;">Operations</th>
                </tr>
            """
            
            for day in history:
                body += f"""
                <tr>
                    <td style="border: 1px solid #ddd; padding: 8px;">{day['date']}</td>
                    <td style="border: 1px solid #ddd; padding: 8px;">{day['total_cost']:,} units</td>
                    <td style="border: 1px solid #ddd; padding: 8px;">{day['operations']}</td>
                </tr>
                """
            
            body += """
            </table>
            
            <p><strong>Note:</strong> This data has been archived and will be removed from the database to save space.</p>
            """
            
            return notifications.send_email_notification(subject, body)
            
        except Exception as e:
            print(f"Error sending history email: {e}")
            return False
    
    def cleanup_old_history(self, keep_days: int = 7) -> bool:
        """Clean up old quota history after sending email backup"""
        try:
            # Send email backup first
            self.send_history_email(keep_days)
            
            # Clean up old data
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                DELETE FROM quota_logs 
                WHERE timestamp < datetime('now', '-{} days')
            """.format(keep_days))
            
            deleted_count = cursor.rowcount
            conn.commit()
            conn.close()
            
            print(f"Cleaned up {deleted_count} old quota log entries")
            return True
            
        except Exception as e:
            print(f"Error cleaning up history: {e}")
            return False
    
    def optimize_upload_schedule(self) -> Dict:
        """Optimize upload schedule based on quota usage"""
        usage = self.get_quota_usage_estimate()
        safe_uploads = self.get_safe_upload_count()
        
        recommendations = {
            'can_upload_now': self.can_upload(),
            'safe_upload_count': safe_uploads,
            'recommended_uploads_today': min(safe_uploads, Config.VIDEOS_PER_DAY),
            'should_pause': self.should_pause_uploads(),
            'quota_status': usage['status'],
            'next_reset': self._get_next_reset_time()
        }
        
        return recommendations
    
    def _get_next_reset_time(self) -> str:
        """Get next quota reset time (midnight Pacific)"""
        from datetime import datetime, timezone, timedelta
        
        # Pacific Time is UTC-8 (PST) or UTC-7 (PDT)
        # For simplicity, we'll use UTC-8
        pacific_offset = timedelta(hours=-8)
        now_utc = datetime.now(timezone.utc)
        now_pacific = now_utc + pacific_offset
        
        # Next midnight Pacific
        next_midnight = now_pacific.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
        
        return next_midnight.strftime("%Y-%m-%d %H:%M:%S Pacific Time")
