"""
Scheduler for automated video generation and upload
Manages daily video creation tasks
"""
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime, date
import time
from typing import Callable
from config import Config

class VideoScheduler:
    def __init__(self, generation_callback: Callable):
        """
        Initialize scheduler
        
        Args:
            generation_callback: Function to call for each video generation
        """
        self.scheduler = BackgroundScheduler()
        self.generation_callback = generation_callback
        self.videos_per_day = Config.VIDEOS_PER_DAY
    
    def start(self):
        """Start the scheduler"""
        # Calculate intervals - spread videos throughout the day
        hours_per_video = 24 / self.videos_per_day
        
        # Schedule videos at optimal times (when engagement is high)
        # Based on research: 2-4pm, 8-11pm EST are peak times
        optimal_hours = [14, 16, 20, 22]  # 2pm, 4pm, 8pm, 10pm
        
        for i in range(self.videos_per_day):
            hour = optimal_hours[i % len(optimal_hours)]
            
            # Schedule daily at this hour
            self.scheduler.add_job(
                func=self._generate_video,
                trigger=CronTrigger(hour=hour, minute=0),
                id=f'video_generation_{i}',
                replace_existing=True
            )
            
            print(f"Scheduled video generation #{i+1} at {hour:02d}:00 daily")
        
        self.scheduler.start()
        print("Scheduler started - videos will be generated automatically")
    
    def _generate_video(self):
        """Wrapper to call generation callback"""
        try:
            print(f"\n{'='*50}")
            print(f"Starting scheduled video generation at {datetime.now()}")
            print(f"{'='*50}\n")
            
            self.generation_callback()
            
            print(f"\n{'='*50}")
            print(f"Completed video generation at {datetime.now()}")
            print(f"{'='*50}\n")
        except Exception as e:
            print(f"Error in scheduled video generation: {e}")
            import traceback
            traceback.print_exc()
    
    def stop(self):
        """Stop the scheduler"""
        self.scheduler.shutdown()
    
    def update_videos_per_day(self, count: int):
        """Update number of videos per day"""
        self.videos_per_day = count
        self.stop()
        self.start()

