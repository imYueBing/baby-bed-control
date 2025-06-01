import random
import time
from threading import Thread

class MockArduinoController:
    def __init__(self):
        self.subscribers = []

    def get_heart_rate(self):
        # 返回一个随机的心率值
        return random.randint(60, 100)

    def subscribe_heart_rate(self, callback):
        self.subscribers.append(callback)
        # 启动一个线程来模拟心率数据的更新
        Thread(target=self._simulate_heart_rate_updates, daemon=True).start()

    def _simulate_heart_rate_updates(self):
        while True:
            heart_rate = self.get_heart_rate()
            for callback in self.subscribers:
                callback(heart_rate)
            time.sleep(5)  # 每5秒更新一次心率
