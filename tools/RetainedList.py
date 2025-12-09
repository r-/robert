"""
RetainedList - Thread-safe data structure for temporary item retention.

Maintains a list of items with automatic expiration based on frame counts.
Useful for tracking transient detections like QR codes across multiple frames.
"""

import threading
import time
import logging
from typing import List, Dict, Optional

# Logger setup
logger = logging.getLogger(__name__)


class RetainedList:
    """
    A thread-safe list that retains items for a specified number of frames.
    
    Items are retained even after disappearing from the detection stream,
    and are gradually forgotten over subsequent frames.
    
    This is useful for QR code detection where codes may flicker or be
    temporarily obscured but should still be considered "active" for a period.
    
    Attributes:
        retention_frames (int): Number of frames to retain items
        frame_delay (float): Time in seconds between frame updates
    """
    
    def __init__(self, retention_frames: int = 3, frame_delay: float = 0.1):
        """
        Initialize the RetainedList.
        
        Args:
            retention_frames (int): Number of frames to retain each item
            frame_delay (float): Delay in seconds between frame updates
        """
        self.items: Dict[str, int] = {}  # item -> frames remaining
        self.retention_frames = retention_frames
        self.frame_delay = frame_delay
        self.lock = threading.Lock()
        self.running = False
        self.current_items: List[str] = []
        self.thread: Optional[threading.Thread] = None
        
        logger.info(f"RetainedList initialized: retention_frames={retention_frames}, frame_delay={frame_delay}")
    
    def start(self) -> None:
        """
        Start the background thread that manages item expiration.
        """
        if self.running:
            logger.warning("RetainedList is already running")
            return
        
        self.running = True
        self.thread = threading.Thread(
            target=self._run,
            daemon=True,
            name="RetainedList-Expiry"
        )
        self.thread.start()
        logger.info("RetainedList background thread started")
    
    def stop(self) -> None:
        """
        Stop the background thread.
        """
        if not self.running:
            logger.warning("RetainedList is not running")
            return
        
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
        logger.info("RetainedList background thread stopped")
    
    def update_items(self, items: List[str]) -> None:
        """
        Update the list of currently detected items.
        
        Args:
            items (List[str]): New list of detected items
        """
        with self.lock:
            self.current_items = items if items else []
        logger.debug(f"Items updated: {len(self.current_items)} items")
    
    def get_items(self) -> List[str]:
        """
        Get the current list of active items.
        
        Returns:
            List[str]: List of items still in retention
        """
        with self.lock:
            return list(self.items.keys())
    
    def _run(self) -> None:
        """
        Background thread loop that manages item expiration.
        
        Periodically updates retention counters:
        - Items in current_items get full retention reset
        - Items not in current_items decrement their counters
        - Items with 0 counter are removed
        """
        logger.info("RetainedList expiry loop started")
        
        try:
            while self.running:
                with self.lock:
                    # Reset countdown for items still present
                    for item in self.current_items:
                        self.items[item] = self.retention_frames
                    
                    # Decrement countdown for stale items
                    to_delete = []
                    for item, count in self.items.items():
                        if item not in self.current_items:
                            self.items[item] -= 1
                            if self.items[item] <= 0:
                                to_delete.append(item)
                    
                    # Remove expired items
                    for item in to_delete:
                        del self.items[item]
                        logger.debug(f"Item expired: {item}")
                
                # Sleep before next cycle
                time.sleep(self.frame_delay)
                
        except Exception as e:
            logger.error(f"Error in RetainedList expiry loop: {e}")
        finally:
            logger.info("RetainedList expiry loop stopped")
