#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
床体控制器模块 - 负责控制婴儿床的升降
"""

import logging
from .base_controller import BaseArduinoController

# 配置日志
logger = logging.getLogger(__name__)

class BedController(BaseArduinoController):
    """简化的床体控制器，用于发送UP/DOWN命令并处理简单响应"""
    
    def __init__(self, port, baud_rate=9600, timeout=1):
        """
        初始化床体控制器
        
        Args:
            port (str): 串行端口（例如 '/dev/ttyUSB0'）
            baud_rate (int): 波特率
            timeout (float): 读取超时（秒）
        """
        super().__init__(port, baud_rate, timeout)
        self.last_bed_response = None
        self.current_bed_height = 0 # Add for compatibility if needed by ArduinoController
    
    def _handle_specific_response(self, response_line):
        """处理来自Arduino的特定于床的响应"""
        if response_line.startswith("CONFIRMED:"):
            self.last_bed_response = response_line
            logger.info(f"BedController 确认: {response_line}")
            # Potentially update internal state based on response, e.g., if it was CONFIRMED: UP
        elif response_line.startswith("UNKNOWN_CMD:"):
            logger.warning(f"BedController 收到未知命令回复: {response_line}")
        # Add more specific parsing if Arduino sends back height or other status
    
    def bed_up(self):
        """
        升高床
        
        Returns:
            bool: 命令是否已发送
        """
        logger.info("Send the BED_UP command (simple string)")
        return self.send_command("UP")
    
    def bed_down(self):
        """
        降低床
        
        Returns:
            bool: 命令是否已发送
        """
        logger.info("Send the BED_DOWN command (simple string)")
        return self.send_command("DOWN")
    
    def bed_stop(self):
        logger.info("发送 BED_STOP 命令 (简单字符串，测试Arduino可能不响应)")
        return self.send_command("STOP")
    
    def get_last_response(self):
        return self.last_bed_response

    def get_bed_height(self): # Add for compatibility
        """获取床体当前高度 (简化测试中返回模拟值或最后已知状态)"""
        # For this simple test, Arduino doesn't send height. 
        # We could have it request height via a command if needed.
        # Or, if the confirmation implies a state change, update self.current_bed_height
        logger.debug(f"BedController: get_bed_height() called, returning {self.current_bed_height} (simulated/last known)")
        return self.current_bed_height 