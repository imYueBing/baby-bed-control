#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
床体控制器模块 - 负责控制婴儿床的升降
"""

import logging
from enum import Enum
from .base_controller import BaseArduinoController

# 配置日志
logger = logging.getLogger(__name__)

# 命令类型枚举
class BedCommandType(Enum):
    BED_UP = "BED_UP"
    BED_DOWN = "BED_DOWN"
    BED_STOP = "BED_STOP"
    BED_HEIGHT = "BED_HEIGHT"

class BedController(BaseArduinoController):
    """床体控制器类，负责控制婴儿床的升降"""
    
    def __init__(self, port, baud_rate=9600, timeout=1):
        """
        初始化床体控制器
        
        Args:
            port (str): 串行端口（例如 '/dev/ttyUSB0'）
            baud_rate (int): 波特率
            timeout (float): 读取超时（秒）
        """
        super().__init__(port, baud_rate, timeout)
        
        # 床体当前高度
        self.current_bed_height = None
    
    def _handle_response(self, data):
        """
        处理来自Arduino的响应
        
        Args:
            data (dict): 解析后的JSON响应
        """
        # 检查响应类型
        if 'type' in data:
            if data['type'] == 'BED_HEIGHT':
                # 处理床高数据
                if 'value' in data:
                    self.current_bed_height = data['value']
                    logger.debug(f"床体当前高度: {self.current_bed_height}")
            
            elif data['type'] == 'BED_CONTROL':
                # 处理床控制响应
                logger.debug(f"床体控制响应: {data}")
            
            elif data['type'] == 'SYSTEM_STATUS':
                # 处理系统状态
                if 'bed_height' in data:
                    self.current_bed_height = data['bed_height']
                    logger.debug(f"床体当前高度: {self.current_bed_height}")
    
    def bed_up(self):
        """
        升高床
        
        Returns:
            bool: 命令是否已发送
        """
        logger.info("发送床体上升命令")
        return self.send_command(BedCommandType.BED_UP.value)
    
    def bed_down(self):
        """
        降低床
        
        Returns:
            bool: 命令是否已发送
        """
        logger.info("发送床体下降命令")
        return self.send_command(BedCommandType.BED_DOWN.value)
    
    def bed_stop(self):
        """
        停止床体移动
        
        Returns:
            bool: 命令是否已发送
        """
        logger.info("发送床体停止命令")
        return self.send_command(BedCommandType.BED_STOP.value)
    
    def get_bed_height(self):
        """
        获取床体当前高度
        
        Returns:
            int or None: 床体当前高度，如果未知则为None
        """
        self.send_command(BedCommandType.BED_HEIGHT.value)
        
        # 返回最后已知的高度（异步更新）
        return self.current_bed_height 