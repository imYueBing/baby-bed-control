#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
心率控制器模块 - 负责获取和处理婴儿心率数据
"""

import logging
from enum import Enum
from .base_controller import BaseArduinoController

# 配置日志
logger = logging.getLogger(__name__)

# 命令类型枚举
class HeartRateCommandType(Enum):
    HEART_RATE = "HEART_RATE"
    HEART_RATE_SUBSCRIBE = "HEART_RATE_SUBSCRIBE"
    HEART_RATE_UNSUBSCRIBE = "HEART_RATE_UNSUBSCRIBE"

class HeartRateController(BaseArduinoController):
    """心率控制器类，负责获取和处理婴儿心率数据"""
    
    def __init__(self, port, baud_rate=9600, timeout=1):
        """
        初始化心率控制器
        
        Args:
            port (str): 串行端口（例如 '/dev/ttyUSB0'）
            baud_rate (int): 波特率
            timeout (float): 读取超时（秒）
        """
        super().__init__(port, baud_rate, timeout)
        
        # 心率回调函数列表
        self.heart_rate_callbacks = []
        
        # 最后一次读取的心率值
        self.last_heart_rate = None
    
    def _handle_response(self, data):
        """
        处理来自Arduino的响应
        
        Args:
            data (dict): 解析后的JSON响应
        """
        # 检查响应类型
        if 'type' in data:
            if data['type'] == 'HEART_RATE':
                # 处理心率数据
                if 'value' in data:
                    self.last_heart_rate = data['value']
                    logger.debug(f"收到心率数据: {self.last_heart_rate}")
                    
                    # 通知所有订阅者
                    self._notify_subscribers(self.last_heart_rate)
            
            elif data['type'] == 'SYSTEM_STATUS':
                # 处理系统状态
                if 'heart_rate' in data:
                    self.last_heart_rate = data['heart_rate']
                    logger.debug(f"当前心率: {self.last_heart_rate}")
    
    def _notify_subscribers(self, heart_rate):
        """
        通知所有心率订阅者
        
        Args:
            heart_rate (int): 心率值
        """
        for callback in self.heart_rate_callbacks:
            try:
                callback(heart_rate)
            except Exception as e:
                logger.error(f"心率回调错误: {e}")
    
    def get_heart_rate(self):
        """
        获取当前心率
        
        Returns:
            int or None: 当前心率，如果未知则为None
        """
        self.send_command(HeartRateCommandType.HEART_RATE.value)
        
        # 返回最后已知的心率（异步更新）
        return self.last_heart_rate
    
    def subscribe_heart_rate(self, callback):
        """
        订阅心率数据
        
        Args:
            callback (callable): 当收到新心率数据时调用的回调函数，参数为心率值
        """
        if callback not in self.heart_rate_callbacks:
            self.heart_rate_callbacks.append(callback)
        
        # 如果这是第一个订阅者，启用心率流
        if len(self.heart_rate_callbacks) == 1:
            self.send_command(HeartRateCommandType.HEART_RATE_SUBSCRIBE.value)
    
    def unsubscribe_heart_rate(self, callback):
        """
        取消订阅心率数据
        
        Args:
            callback (callable): 先前注册的回调函数
        """
        if callback in self.heart_rate_callbacks:
            self.heart_rate_callbacks.remove(callback)
        
        # 如果没有更多订阅者，停止心率流
        if len(self.heart_rate_callbacks) == 0:
            self.send_command(HeartRateCommandType.HEART_RATE_UNSUBSCRIBE.value) 