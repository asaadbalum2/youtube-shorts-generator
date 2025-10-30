"""
Email reporting system
Sends daily reports on video generation and performance
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, date
from typing import Dict, List
from core.config import Config
from core.database import Database

class EmailReporter:
    def __init__(self):
        self.email_address = Config.EMAIL_ADDRESS
        self.email_password = Config.EMAIL_PASSWORD
        self.recipient = Config.REPORT_RECIPIENT
        self.db = Database()
    
    def send_daily_report(self):
        """Send daily summary report"""
        today = date.today().isoformat()
        stats = self.db.get_daily_stats(today)
        
        if not stats:
            stats = {
                'videos_created': 0,
                'videos_uploaded': 0,
                'total_views': 0,
                'total_likes': 0
            }
        
        # Create email content
        subject = f"YouTube Shorts Daily Report - {date.today().strftime('%B %d, %Y')}"
        body = self._create_report_body(stats, today)
        
        try:
            self._send_email(subject, body)
            print(f"Daily report sent to {self.recipient}")
        except Exception as e:
            print(f"Error sending email report: {e}")
    
    def send_video_upload_notification(self, video_title: str, video_url: str):
        """Send notification when a video is uploaded"""
        subject = f"New Video Uploaded: {video_title[:50]}"
        body = f"""
        A new YouTube Short has been uploaded!
        
        Title: {video_title}
        URL: {video_url}
        
        Check it out on your channel!
        """
        
        try:
            self._send_email(subject, body)
        except Exception as e:
            print(f"Error sending upload notification: {e}")
    
    def _create_report_body(self, stats: Dict, date_str: str) -> str:
        """Create formatted report body"""
        report_date = datetime.strptime(date_str, "%Y-%m-%d").strftime("%B %d, %Y")
        
        body = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; }}
                .header {{ background-color: #ff0000; color: white; padding: 20px; }}
                .stats {{ padding: 20px; }}
                .stat-item {{ margin: 10px 0; padding: 10px; background-color: #f5f5f5; }}
                .stat-label {{ font-weight: bold; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>📹 YouTube Shorts Generator - Daily Report</h1>
                <p>Date: {report_date}</p>
            </div>
            
            <div class="stats">
                <h2>Today's Statistics</h2>
                
                <div class="stat-item">
                    <span class="stat-label">Videos Created:</span>
                    <span>{stats['videos_created']}</span>
                </div>
                
                <div class="stat-item">
                    <span class="stat-label">Videos Uploaded:</span>
                    <span>{stats['videos_uploaded']}</span>
                </div>
                
                <div class="stat-item">
                    <span class="stat-label">Total Views:</span>
                    <span>{stats['total_views']:,}</span>
                </div>
                
                <div class="stat-item">
                    <span class="stat-label">Total Likes:</span>
                    <span>{stats['total_likes']:,}</span>
                </div>
                
                <div class="stat-item">
                    <span class="stat-label">Average Views per Video:</span>
                    <span>{stats['total_views'] // max(stats['videos_uploaded'], 1):,}</span>
                </div>
            </div>
            
            <div style="padding: 20px; margin-top: 20px; background-color: #e8f4f8;">
                <p><strong>Note:</strong> This is an automated report from your YouTube Shorts Generator.</p>
                <p>The system is running autonomously and will continue generating videos daily.</p>
            </div>
        </body>
        </html>
        """
        
        return body
    
    def _send_email(self, subject: str, body: str):
        """Send email via SMTP"""
        if not self.email_address or not self.email_password:
            print("Email credentials not configured")
            return
        
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = self.email_address
        msg['To'] = self.recipient
        
        # Attach HTML body
        html_part = MIMEText(body, 'html')
        msg.attach(html_part)
        
        # Send via Gmail SMTP
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(self.email_address, self.email_password)
            server.send_message(msg)

