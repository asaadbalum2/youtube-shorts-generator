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
        """Start the scheduler with randomized posting times (prevents YouTube spam detection)"""
        import random
        
        # Optimal hour ranges for engagement - randomized within these windows
        # This prevents YouTube from detecting patterns
        optimal_hour_ranges = [
            (13, 15),  # 1pm-3pm (afternoon)
            (15, 17),  # 3pm-5pm (afternoon) 
            (19, 21),  # 7pm-9pm (evening)
            (20, 22),  # 8pm-10pm (evening)
        ]
        
        for i in range(self.videos_per_day):
            # Pick random time within optimal ranges
            hour_range = optimal_hour_ranges[i % len(optimal_hour_ranges)]
            
            # Randomize hour within range
            hour = random.randint(hour_range[0], hour_range[1])
            
            # Randomize minute (0-59) for more variation - prevents pattern detection
            minute = random.randint(0, 59)
            
            # Schedule daily at this randomized time
            self.scheduler.add_job(
                func=self._generate_video,
                trigger=CronTrigger(hour=hour, minute=minute),
                id=f'video_generation_{i}',
                replace_existing=True
            )
            
            print(f"Scheduled video generation #{i+1} at {hour:02d}:{minute:02d} daily (randomized to prevent spam detection)")
        
        self.scheduler.start()
        print("Scheduler started - videos will be generated automatically at randomized times")
    
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

