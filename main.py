"""
Main application entry point
Orchestrates video generation, upload, and scheduling
"""
import os
import sys
import logging
from datetime import datetime, date
from typing import Optional
import traceback

from core.config import Config
from core.database import Database
from core.topic_discovery import TopicDiscoveryAgent
from core.content_generator import ContentGenerator
from core.video_creator import VideoCreator
from core.youtube_uploader import YouTubeUploader
from core.scheduler import VideoScheduler
from core.email_reporter import EmailReporter
from fastapi import FastAPI
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles

# Setup logging
logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('shorts_generator.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

class YouTubeShortsGenerator:
    def __init__(self):
        self.db = Database()
        self.topic_agent = TopicDiscoveryAgent()
        self.content_generator = ContentGenerator()
        self.video_creator = VideoCreator()
        self.youtube_uploader = YouTubeUploader()
        self.email_reporter = EmailReporter()
        self.scheduler = None
        
        logger.info("YouTube Shorts Generator initialized")
    
    def retry_failed_upload(self, max_retries: int = 3) -> Optional[dict]:
        """
        Retry uploading a video that previously failed
        
        Returns: Video info dict or None if failed
        """
        try:
            # First, try to find and update file paths for existing videos
            videos_without_paths = self.db.get_videos_without_file_path()
            for video in videos_without_paths:
                video_id = video['video_id']
                # Try to find the video file in output directory
                possible_paths = [
                    f"./output/short_{video_id}.mp4",
                    f"./output/{video_id}.mp4",
                    f"./output/{video_id}",
                ]
                # Also try to match by partial video_id
                import glob
                matching_files = glob.glob(f"./output/*{video_id}*.mp4")
                if matching_files:
                    file_path = matching_files[0]
                    self.db.update_video_file_path(video_id, file_path)
                    logger.info(f"Found and updated file path for {video_id}: {file_path}")
            
            # Get failed uploads (now with updated paths)
            failed_videos = self.db.get_failed_uploads(max_retries=max_retries)
            
            if not failed_videos:
                logger.info("No failed uploads to retry")
                return None
            
            # Try the oldest failed upload
            video_data = failed_videos[0]
            video_path = video_data['video_file_path']
            
            # If still no path, try to find it
            if not video_path:
                video_id = video_data['video_id']
                import glob
                matching_files = glob.glob(f"./output/*{video_id}*.mp4")
                if matching_files:
                    video_path = matching_files[0]
                    self.db.update_video_file_path(video_id, video_path)
                    logger.info(f"Found video file: {video_path}")
            
            if not video_path or not os.path.exists(video_path):
                logger.warning(f"Video file not found: {video_path}, skipping")
                return None
            
            logger.info(f"Retrying upload for video: {video_data['title']}")
            logger.info(f"File: {video_path}")
            
            # Retry upload
            upload_result = self.youtube_uploader.upload_video(
                video_path=video_path,
                title=video_data['title'],
                description=video_data['description'],
                tags=[]
            )
            
            if upload_result:
                # Update database
                self.db.update_video_upload(
                    video_id=video_data['video_id'],
                    youtube_url=upload_result['url']
                )
                
                today = date.today().isoformat()
                self.db.update_daily_stats(today, videos_uploaded=1)
                
                logger.info(f"✅ Successfully retried upload: {upload_result['url']}")
                return upload_result
            else:
                # If upload failed, mark it for retry and provide helpful error message
                error_msg = str(e)
                if 'expired' in error_msg.lower() or 'token' in error_msg.lower():
                    logger.error("⚠️ YouTube token expired. Run 'python scripts/regenerate_youtube_token.py' in Replit Shell to fix.")
                    logger.error("Video will be retried automatically once token is regenerated.")
                return None
                
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Error retrying upload: {e}")
            
            # Provide helpful guidance for token issues
            if 'expired' in error_msg.lower() or 'token' in error_msg.lower() or '401' in error_msg or 'unauthorized' in error_msg.lower():
                logger.error("\n" + "="*60)
                logger.error("TOKEN EXPIRATION DETECTED")
                logger.error("="*60)
                logger.error("To fix:")
                logger.error("1. Run: python scripts/regenerate_youtube_token.py")
                logger.error("2. Update YOUTUBE_REFRESH_TOKEN in Replit Secrets")
                logger.error("3. Restart the app")
                logger.error("="*60 + "\n")
            
            import traceback
            logger.error(traceback.format_exc())
            return None
    
    def generate_and_upload_video(self, retry_failed_first: bool = True) -> Optional[dict]:
        """
        Main workflow: Generate one video and upload it
        Optionally retries failed uploads first before generating new video
        
        Returns: Video info dict or None if failed
        """
        # First, try to retry a failed upload if any exist
        if retry_failed_first:
            logger.info("Checking for failed uploads to retry...")
            retry_result = self.retry_failed_upload()
            if retry_result:
                logger.info("Successfully retried a failed upload, skipping new generation")
                return retry_result
            logger.info("No failed uploads to retry, generating new video...")
        
        try:
            logger.info("=" * 60)
            logger.info("Starting video generation workflow")
            logger.info("=" * 60)
            
            # Step 1: Discover trending topic
            logger.info("Step 1: Discovering trending topic...")
            topic_data = self.topic_agent.select_best_topic()
            
            if not topic_data:
                logger.error("No suitable topic found")
                return None
            
            topic = topic_data['topic']
            trend_score = topic_data['score']
            logger.info(f"Selected topic: {topic} (Score: {trend_score})")
            
            # Save trend to database
            self.db.add_trend(
                topic=topic,
                source=topic_data.get('source', 'unknown'),
                score=trend_score,
                metadata=topic_data.get('metadata', {})
            )
            
            # Step 2: Generate content
            logger.info("Step 2: Generating video content...")
            content = self.content_generator.generate_video_content(topic)
            logger.info(f"Generated title: {content['title']}")
            
            # Step 3: Create video
            logger.info("Step 3: Creating video file...")
            video_path = self.video_creator.create_video(content, topic)
            logger.info(f"Video created: {video_path}")
            
            # Step 4: Save video to database
            video_id = os.path.basename(video_path).replace('.mp4', '')
            video_db_data = {
                'video_id': video_id,
                'title': content['title'],
                'description': content['description'],
                'topic': topic,
                'trend_score': trend_score,
                'status': 'created',
                'video_file_path': video_path
            }
            self.db.add_video(video_db_data)
            
            # Step 5: Upload to YouTube
            logger.info("Step 4: Uploading to YouTube...")
            try:
                upload_result = self.youtube_uploader.upload_video(
                    video_path=video_path,
                    title=content['title'],
                    description=content['description'],
                    tags=content.get('tags', [])
                )
                
                if upload_result:
                    # Update database
                    self.db.update_video_upload(
                        video_id=video_id,
                        youtube_url=upload_result['url']
                    )
                    
                    # Update daily stats
                    today = date.today().isoformat()
                    self.db.update_daily_stats(
                        today,
                        videos_created=1,
                        videos_uploaded=1
                    )
                    
                    # Send email notification
                    self.email_reporter.send_video_upload_notification(
                        content['title'],
                        upload_result['url']
                    )
                    
                    logger.info(f"Successfully uploaded: {upload_result['url']}")
                    return upload_result
                else:
                    logger.error("Upload failed - no result returned")
            
            except Exception as upload_error:
                logger.error(f"Upload error: {upload_error}")
                logger.error(traceback.format_exc())
                
                # Check if it's a recoverable error
                from core.error_recovery import ErrorRecovery
                if ErrorRecovery.handle_api_error(upload_error, "YouTube", max_retries=1):
                    logger.info("Attempting automatic recovery...")
                    # Retry upload once after error recovery
                    try:
                        upload_result = self.youtube_uploader.upload_video(
                            video_path=video_path,
                            title=content['title'],
                            description=content['description'],
                            tags=content.get('tags', [])
                        )
                        if upload_result:
                            self.db.update_video_upload(video_id, upload_result['url'])
                            today = date.today().isoformat()
                            self.db.update_daily_stats(today, videos_created=1, videos_uploaded=1)
                            logger.info(f"✅ Recovery successful: {upload_result['url']}")
                            return upload_result
                    except Exception as retry_error:
                        logger.error(f"Recovery attempt failed: {retry_error}")
                
                # Video was created but upload failed - save for retry
                error_msg = str(upload_error)
                self.db.mark_upload_failed(video_id, error_msg)
                
                # Check if it's a token expiration issue - send alert
                if 'invalid_grant' in error_msg.lower() or 'expired' in error_msg.lower():
                    try:
                        from email_reporter import EmailReporter
                        emailer = EmailReporter()
                        emailer._send_email(
                            subject="🚨 YouTube Token Expired - Action Required",
                            body=f"""
                            <h2>YouTube Token Expiration Alert</h2>
                            <p>Your YouTube refresh token has expired and needs regeneration.</p>
                            <p><strong>Error:</strong> {error_msg[:200]}</p>
                            <p><strong>To fix:</strong></p>
                            <ol>
                                <li>In Replit Shell, run: <code>python regenerate_youtube_token.py</code></li>
                                <li>Follow the prompts to get a new refresh token</li>
                                <li>Update YOUTUBE_REFRESH_TOKEN in Replit Secrets</li>
                                <li>Restart the app</li>
                                <li>Pending videos will automatically retry once token is fixed</li>
                            </ol>
                            <p>The system will continue creating videos but uploads will fail until token is regenerated.</p>
                            """
                        )
                        logger.info("Email alert sent about token expiration")
                    except Exception as email_error:
                        logger.warning(f"Could not send email alert: {email_error}")
                
                # Update stats
                today = date.today().isoformat()
                self.db.update_daily_stats(today, videos_created=1)
                
                logger.warning(f"Video created but upload failed. Saved to retry queue. Error: {error_msg[:100]}")
            
            return None
        
        except Exception as e:
            logger.error(f"Error in video generation workflow: {e}")
            logger.error(traceback.format_exc())
            
            # Log error but don't crash - system should continue running
            import traceback as tb
            logger.error(f"Full traceback: {tb.format_exc()}")
            
            return None
    
    def start_autonomous_mode(self, start_web_server=True):
        """Start fully autonomous operation with scheduled generation"""
        logger.info("Starting autonomous mode...")
        
        # Create scheduler
        self.scheduler = VideoScheduler(self.generate_and_upload_video)
        self.scheduler.start()
        
        # Schedule daily report email (evening)
        from apscheduler.schedulers.background import BackgroundScheduler
        report_scheduler = BackgroundScheduler()
        report_scheduler.add_job(
            func=self.email_reporter.send_daily_report,
            trigger='cron',
            hour=22,  # 10 PM
            minute=0
        )
        report_scheduler.start()
        
        logger.info("Autonomous mode active - system will run continuously")
        
        # Start web server for manual triggers (if requested)
        if start_web_server:
            try:
                app = FastAPI(title="YouTube Shorts Generator API")
                
                @app.get("/")
                def root():
                    return {
                        "status": "YouTube Shorts Generator is running",
                        "videos_per_day": Config.VIDEOS_PER_DAY,
                        "endpoints": {
                            "generate": "POST /generate - Trigger manual video generation",
                            "retry_upload": "POST /retry-upload - Retry failed upload",
                            "failed_uploads": "GET /failed-uploads - List failed uploads",
                            "health": "GET /health - Check system health"
                        }
                    }
                
                @app.post("/generate")
                def trigger_generation():
                    """Manual trigger to generate one video now (for testing)"""
                    try:
                        logger.info("Manual video generation triggered via API")
                        # Run in background thread to avoid blocking
                        import threading
                        def generate_async():
                            self.generate_and_upload_video()
                        
                        thread = threading.Thread(target=generate_async, daemon=True)
                        thread.start()
                        
                        return {
                            "status": "success",
                            "message": "Video generation started in background - check logs for progress"
                        }
                    except Exception as e:
                        logger.error(f"Manual generation error: {e}")
                        return {"status": "error", "message": str(e)}
                
                @app.post("/retry-upload")
                def retry_failed_upload():
                    """Retry uploading a failed video"""
                    try:
                        logger.info("Manual retry of failed upload triggered via API")
                        import threading
                        def retry_async():
                            self.retry_failed_upload()
                        
                        thread = threading.Thread(target=retry_async, daemon=True)
                        thread.start()
                        
                        return {
                            "status": "success",
                            "message": "Retry upload started in background - check logs for progress"
                        }
                    except Exception as e:
                        logger.error(f"Retry upload error: {e}")
                        return {"status": "error", "message": str(e)}
                
                @app.get("/failed-uploads")
                def get_failed_uploads():
                    """Get list of failed uploads"""
                    try:
                        failed = self.db.get_failed_uploads(max_retries=10)
                        return {
                            "status": "success",
                            "count": len(failed),
                            "failed_uploads": [
                                {
                                    "video_id": v['video_id'],
                                    "title": v['title'],
                                    "topic": v['topic'],
                                    "retry_count": v['retry_count'],
                                    "error": v['upload_error'][:100] if v['upload_error'] else ""
                                }
                                for v in failed
                            ]
                        }
                    except Exception as e:
                        return {"status": "error", "message": str(e)}
                
                @app.get("/health")
                def health():
                    return {
                        "status": "healthy",
                        "scheduler_running": self.scheduler is not None,
                        "videos_per_day": Config.VIDEOS_PER_DAY
                    }
                
                # Mount web UI dashboard
                try:
                    from web.web_ui import app as dashboard_app
                    # app.mount() is built-in to FastAPI, no import needed
                    app.mount("/dashboard", dashboard_app)
                    logger.info("Web UI dashboard mounted at /dashboard")
                except Exception as ui_error:
                    logger.warning(f"Could not mount web UI dashboard: {ui_error}")
                    logger.info("Dashboard is optional - API endpoints still work")
                
                # Start FastAPI server in background thread
                import threading
                def run_server():
                    import uvicorn
                    # Use port from env or default to 8080 (Replit uses PORT env var)
                    port = int(os.getenv("PORT", 8080))
                    uvicorn.run(app, host="0.0.0.0", port=port, log_level="warning")
                
                server_thread = threading.Thread(target=run_server, daemon=True)
                server_thread.start()
                logger.info("Web server started on port 8080")
                logger.info("  - Dashboard: https://fba4b05c-3ab8-466c-9cfc-bc8cc6378b68-00-24shrkm35btwt.pike.replit.dev/dashboard")
                logger.info("  - Manual trigger: POST /generate")
                logger.info("  - Health: GET /health")
            except Exception as e:
                logger.warning(f"Could not start web server (this is optional): {e}")
        
        # Keep script running
        try:
            while True:
                import time
                time.sleep(60)  # Sleep and check every minute
        except KeyboardInterrupt:
            logger.info("Shutting down...")
            if self.scheduler:
                self.scheduler.stop()
            report_scheduler.shutdown()
    
    def generate_batch(self, count: Optional[int] = None):
        """Generate a batch of videos immediately"""
        if count is None:
            count = Config.VIDEOS_PER_DAY
        
        logger.info(f"Generating batch of {count} videos...")
        
        results = []
        for i in range(count):
            logger.info(f"\n--- Video {i+1}/{count} ---\n")
            result = self.generate_and_upload_video()
            results.append(result)
            
            if i < count - 1:
                # Wait between videos to avoid rate limits
                import time
                logger.info("Waiting 5 minutes before next video...")
                time.sleep(300)
        
        logger.info(f"\nBatch complete: {len([r for r in results if r])}/{count} videos uploaded")
        
        # Send daily report
        self.email_reporter.send_daily_report()
        
        return results

def main():
    """Main entry point"""
    generator = YouTubeShortsGenerator()
    
    # Check command line arguments
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "batch":
            count = int(sys.argv[2]) if len(sys.argv) > 2 else None
            generator.generate_batch(count)
        elif command == "single":
            generator.generate_and_upload_video()
        elif command == "autonomous":
            generator.start_autonomous_mode()
        else:
            print("Usage:")
            print("  python main.py autonomous  # Start autonomous mode (default)")
            print("  python main.py batch [count]  # Generate batch of videos")
            print("  python main.py single  # Generate one video")
    else:
        # Default: autonomous mode
        generator.start_autonomous_mode()

if __name__ == "__main__":
    main()

