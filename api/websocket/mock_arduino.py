import random
import time
from threading import Thread, Event

class MockArduinoController:
    def __init__(self):
        self.subscribers = []
        self._stop_event = Event()
        self._thread = None

    def get_heart_rate(self):
        # Return a random heart rate value
        return random.randint(60, 100)

    def subscribe_heart_rate(self, callback):
        self.subscribers.append(callback)
        # Only start the thread once
        if self._thread is None or not self._thread.is_alive():
            self._stop_event.clear()
            self._thread = Thread(target=self._simulate_heart_rate_updates, daemon=True)
            self._thread.start()

    def _simulate_heart_rate_updates(self):
        while not self._stop_event.is_set():
            heart_rate = self.get_heart_rate()
            for callback in self.subscribers:
                callback(heart_rate)
            time.sleep(5)  # Update heart rate every 5 seconds

    def stop(self):
        """Stop simulation thread"""
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=1)
