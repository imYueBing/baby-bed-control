#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
心率控制器模块 - 负责获取和处理婴儿心率数据
"""

import logging
import threading
import time
from .base_controller import BaseArduinoController

# 配置日志
logger = logging.getLogger(__name__)

class HeartRateController(BaseArduinoController):
    """简化的心率监测器，模拟定期请求并处理简单响应"""
    
    def __init__(self, port, baud_rate=9600, timeout=1):
        """
        初始化心率控制器
        
        Args:
            port (str): 串行端口（例如 '/dev/ttyUSB0'）
            baud_rate (int): 波特率
            timeout (float): 读取超时（秒）
        """
        super().__init__(port, baud_rate, timeout)
        self.current_heart_rate = None
        self.last_heart_rate_response = None
        self._subscribers = []
        self._monitoring_thread = None
        self._stop_monitoring = threading.Event() # Event to signal thread to stop
        self.consecutive_failures = 0
        self.max_failures = 5
        self.monitoring_interval = 10 # seconds
    
    def _handle_specific_response(self, response_line):
        """处理来自Arduino的特定于心率的响应"""
        if response_line.startswith("HEART_RATE_DATA:"):
            try:
                rate_str = response_line.split(":")[1]
                self.current_heart_rate = int(rate_str)
                self.last_heart_rate_response = response_line
                self.consecutive_failures = 0 # Reset failures on successful response
                logger.info(f"心率更新: {self.current_heart_rate} BPM")
                self._notify_subscribers(self.current_heart_rate)
            except (IndexError, ValueError) as e:
                logger.warning(f"解析心率数据失败 '{response_line}': {e}")
                self.consecutive_failures += 1
        elif response_line.startswith("UNKNOWN_CMD:"):
            logger.warning(f"HeartRateController 收到未知命令回复: {response_line}")
            self.consecutive_failures += 1 # Count as failure if Arduino doesn't understand GetHeartRate
        else:
            # If it's some other response not recognized, also count as a failure for heart rate check
            logger.debug(f"HeartRateController收到非预期响应: {response_line}")
            self.consecutive_failures += 1 
    
    def _notify_subscribers(self, heart_rate):
        """
        通知所有心率订阅者
        
        Args:
            heart_rate (int): 心率值
        """
        for callback in self._subscribers:
            try:
                callback(heart_rate)
            except Exception as e:
                logger.error(f"调用心率订阅者回调时出错: {e}")
    
    def get_heart_rate(self):
        """获取当前心率 (将通过后台线程更新)"""
        # For this simple test, actual request might be initiated by the monitor thread
        # or an explicit call like this could also send a one-off request.
        # Let's make it request directly for now for simplicity if not monitoring.
        if not self._monitoring_thread or not self._monitoring_thread.is_alive():
             logger.debug("非监控模式下请求一次性心率...")
             self.send_command("GET_HEART_RATE")
        return self.current_heart_rate
    
    def subscribe_heart_rate(self, callback):
        """
        订阅心率数据
        
        Args:
            callback (callable): 当收到新心率数据时调用的回调函数，参数为心率值
        """
        if callback not in self._subscribers:
            self._subscribers.append(callback)
        self.start_monitoring() # Start monitoring when first subscriber is added
    
    def unsubscribe_heart_rate(self, callback):
        """
        取消订阅心率数据
        
        Args:
            callback (callable): 先前注册的回调函数
        """
        if callback in self._subscribers:
            self._subscribers.remove(callback)
        if not self._subscribers: # Stop monitoring if no subscribers left
            self.stop_monitoring()
    
    def _monitoring_loop(self):
        logger.info("启动心率监测循环...")
        while not self._stop_monitoring.is_set():
            if not self.is_connected:
                logger.warning("心率监测：Arduino未连接，暂停。")
                self.consecutive_failures +=1 # Increment failures if not connected
            else:
                logger.debug("心率监测：发送GET_HEART_RATE命令")
                success = self.send_command("GET_HEART_RATE")
                if not success:
                    self.consecutive_failures += 1
                # Response processing and failure counting will happen in _handle_specific_response
            
            if self.consecutive_failures >= self.max_failures:
                logger.error(f"连续 {self.max_failures} 次未能获取有效心率响应，停止监测。")
                self.stop_monitoring() # This will set the event and loop will exit
                break # Exit loop immediately

            # Wait for the next interval, checking the stop event frequently
            self._stop_monitoring.wait(self.monitoring_interval)
        logger.info("心率监测循环已停止。")

    def start_monitoring(self):
        if self._monitoring_thread and self._monitoring_thread.is_alive():
            logger.debug("心率监测已在运行中。")
            return
        if not self.is_connected:
            logger.warning("无法启动心率监测：Arduino未连接。")
            return
            
        self._stop_monitoring.clear() # Clear stop event before starting
        self.consecutive_failures = 0 # Reset failure counter
        self._monitoring_thread = threading.Thread(target=self._monitoring_loop)
        self._monitoring_thread.daemon = True
        self._monitoring_thread.start()

    def stop_monitoring(self):
        logger.info("正在停止心率监测...")
        self._stop_monitoring.set() # Signal the thread to stop
        # Joining the thread will be handled by the main close() method if necessary

    def close(self):
        self.stop_monitoring() # Ensure monitoring stops
        if self._monitoring_thread and self._monitoring_thread.is_alive():
             logger.debug("等待心率监测线程结束...")
             self._monitoring_thread.join(timeout=2) # Wait for thread to finish
        super().close() # Call parent's close method 