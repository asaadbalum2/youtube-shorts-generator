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

from config import Config
from database import Database
from topic_discovery import TopicDiscoveryAgent
from content_generator import ContentGenerator
from video_creator import VideoCreator
from youtube_uploader import YouTubeUploader
from scheduler import VideoScheduler
from email_reporter import EmailReporter
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
    
    def generate_and_upload_video(self) -> Optional[dict]:
        """
        Main workflow: Generate one video and upload it
        
        Returns: Video info dict or None if failed
        """
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
                'status': 'created'
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
                from error_recovery import ErrorRecovery
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
                
                # Video was created but upload failed - update stats
                today = date.today().isoformat()
                self.db.update_daily_stats(today, videos_created=1)
                
                logger.warning("Video created but upload failed. Will retry on next scheduled run.")
            
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
                
                @app.get("/health")
                def health():
                    return {
                        "status": "healthy",
                        "scheduler_running": self.scheduler is not None,
                        "videos_per_day": Config.VIDEOS_PER_DAY
                    }
                
                # Mount web UI dashboard
                try:
                    from web_ui import app as dashboard_app
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
                    uvicorn.run(app, host="0.0.0.0", port=8080, log_level="warning")
                
                server_thread = threading.Thread(target=run_server, daemon=True)
                server_thread.start()
                logger.info("Web server started on port 8080")
                logger.info("  - Dashboard: http://your-repl-url.repl.co/dashboard")
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

