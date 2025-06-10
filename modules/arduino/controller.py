#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Arduino控制器模块 - 整合床体控制和心率监测功能
"""

import logging
from .bed_controller import BedController
from .heart_rate_controller import HeartRateController
from utils.device_discovery import discover_arduino_device

# 配置日志
logger = logging.getLogger(__name__)

class ArduinoController:
    """
    Arduino控制器类，整合床体控制和心率监测功能
    
    这个类是一个façade（外观模式），简化了与Arduino的交互，
    内部使用专门的控制器处理不同类型的功能
    """
    
    def __init__(self, port=None, baud_rate=9600, timeout=1):
        """
        初始化Arduino控制器
        
        Args:
            port (str, optional): 串行端口，如果为None则自动发现
            baud_rate (int): 波特率
            timeout (float): 读取超时（秒）
        """
        # 如果没有指定端口，尝试自动发现
        if port is None:
            port = discover_arduino_device(baud_rate)
            if port:
                logger.info(f"自动发现Arduino设备: {port}")
            else:
                logger.warning("未找到Arduino设备，将使用模拟设备")
                port = "/dev/ttyNONEXISTENT"  # 使用不存在的端口，控制器将进入离线模式
        
        # 创建专门的控制器
        self.bed_controller = BedController(port, baud_rate, timeout)
        self.heart_rate_controller = HeartRateController(port, baud_rate, timeout)
        
        # 控制器连接状态
        self.is_connected = (self.bed_controller.is_connected and 
                            self.heart_rate_controller.is_connected)
    
    # --------- 床体控制相关方法 ---------
    
    def bed_up(self):
        """
        整体升高床
        
        Returns:
            bool: 命令是否已发送
        """
        return self.bed_controller.bed_up()
    
    def bed_down(self):
        """
        整体降低床
        
        Returns:
            bool: 命令是否已发送
        """
        return self.bed_controller.bed_down()
    
    def bed_stop(self):
        """
        整体停止床体移动
        
        Returns:
            bool: 命令是否已发送
        """
        return self.bed_controller.bed_stop()
    
    def left_up(self):
        """
        左侧升高床
        
        Returns:
            bool: 命令是否已发送
        """
        return self.bed_controller.left_up()
    
    def left_down(self):
        """
        左侧降低床
        
        Returns:
            bool: 命令是否已发送
        """
        return self.bed_controller.left_down()
    
    def left_stop(self):
        """
        左侧停止床体移动
        
        Returns:
            bool: 命令是否已发送
        """
        return self.bed_controller.left_stop()
    
    def right_up(self):
        """
        右侧升高床
        
        Returns:
            bool: 命令是否已发送
        """
        return self.bed_controller.right_up()
    
    def right_down(self):
        """
        右侧降低床
        
        Returns:
            bool: 命令是否已发送
        """
        return self.bed_controller.right_down()
    
    def right_stop(self):
        """
        右侧停止床体移动
        
        Returns:
            bool: 命令是否已发送
        """
        return self.bed_controller.right_stop()
    
    def get_bed_status(self):
        """
        获取床体当前状态
        
        Returns:
            dict: 床体状态信息
        """
        return self.bed_controller.get_bed_status()
    
    def get_bed_height(self):
        """
        获取床体当前高度 (为兼容旧API保留)
        
        Returns:
            dict: 床体状态信息
        """
        return self.get_bed_status()
    
    # --------- 心率监测相关方法 ---------
    
    def get_heart_rate(self):
        """
        获取当前心率
        
        Returns:
            int or None: 当前心率，如果未知则为None
        """
        return self.heart_rate_controller.get_heart_rate()
    
    def subscribe_heart_rate(self, callback):
        """
        订阅心率数据
        
        Args:
            callback (callable): 当收到新心率数据时调用的回调函数，参数为心率值
        """
        self.heart_rate_controller.subscribe_heart_rate(callback)
    
    def unsubscribe_heart_rate(self, callback):
        """
        取消订阅心率数据
        
        Args:
            callback (callable): 先前注册的回调函数
        """
        self.heart_rate_controller.unsubscribe_heart_rate(callback)
    
    # --------- 通用方法 ---------
    
    def close(self):
        """关闭所有控制器连接"""
        self.bed_controller.close()
        self.heart_rate_controller.close()
    
    def get_system_status(self):
        """
        获取系统状态
        
        Returns:
            dict: 系统状态信息
        """
        return {
            'bed_height': self.get_bed_height(),
            'heart_rate': self.get_heart_rate()
        } 