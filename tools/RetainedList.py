import threading
import time

class RetainedList:
    def __init__(self, retention_frames=3, frame_delay=0.1):
        self.items = {}  # key: item, value: frames remaining
        self.retention_frames = retention_frames
        self.frame_delay = frame_delay  # Time between frames in seconds
        self.lock = threading.Lock()
        self.running = False
        self.current_items = []

    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()

    def stop(self):
        self.running = False
        self.thread.join()

    def update_items(self, items):
        with self.lock:
            self.current_items = items

    def get_items(self):
        with self.lock:
            return list(self.items.keys())

    def _run(self):
        while self.running:
            with self.lock:
                # Reset countdown for items still present
                for item in self.current_items:
                    self.items[item] = self.retention_frames

                # Decrement countdown for stale items
                to_delete = []
                for item in self.items:
                    if item not in self.current_items:
                        self.items[item] -= 1
                        if self.items[item] <= 0:
                            to_delete.append(item)

                for item in to_delete:
                    del self.items[item]
            time.sleep(self.frame_delay)
