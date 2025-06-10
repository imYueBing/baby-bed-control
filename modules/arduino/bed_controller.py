#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
床体控制器模块 - 负责控制婴儿床的升降，支持左右独立控制
"""

import logging
from .base_controller import BaseArduinoController

# 配置日志
logger = logging.getLogger(__name__)

class BedController(BaseArduinoController):
    """床体控制器，支持整体控制和左右独立控制"""
    
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
        self.left_status = "stopped"  # 左侧状态: "up", "down", "stopped"
        self.right_status = "stopped" # 右侧状态: "up", "down", "stopped"
    
    def _handle_specific_response(self, response_line):
        """处理来自Arduino的特定于床的响应"""
        if response_line.startswith("CONFIRMED:"):
            self.last_bed_response = response_line
            logger.info(f"BedController 确认: {response_line}")
            
            # 更新内部状态
            action = response_line.replace("CONFIRMED:", "").strip()
            self._update_bed_status(action)
            
        elif response_line.startswith("UNKNOWN_CMD:"):
            logger.warning(f"BedController 收到未知命令回复: {response_line}")
        elif "STATUS" in response_line:
            logger.info(f"BedController 状态更新: {response_line}")
            # 可以在这里解析状态信息，如果需要
    
    def _update_bed_status(self, action):
        """根据确认的动作更新床体状态"""
        if action == "UP":
            self.left_status = "up"
            self.right_status = "up"
        elif action == "DOWN":
            self.left_status = "down"
            self.right_status = "down"
        elif action == "STOP":
            self.left_status = "stopped"
            self.right_status = "stopped"
        elif action == "LEFT_UP":
            self.left_status = "up"
        elif action == "LEFT_DOWN":
            self.left_status = "down"
        elif action == "LEFT_STOP":
            self.left_status = "stopped"
        elif action == "RIGHT_UP":
            self.right_status = "up"
        elif action == "RIGHT_DOWN":
            self.right_status = "down"
        elif action == "RIGHT_STOP":
            self.right_status = "stopped"
    
    # --------- 整体控制方法 ---------
    
    def bed_up(self):
        """
        整体升高床
        
        Returns:
            bool: 命令是否已发送
        """
        logger.info("发送整体上升命令 UP")
        return self.send_command("UP")
    
    def bed_down(self):
        """
        整体降低床
        
        Returns:
            bool: 命令是否已发送
        """
        logger.info("发送整体下降命令 DOWN")
        return self.send_command("DOWN")
    
    def bed_stop(self):
        """
        整体停止床体移动
        
        Returns:
            bool: 命令是否已发送
        """
        logger.info("发送整体停止命令 STOP")
        return self.send_command("STOP")
    
    # --------- 左侧控制方法 ---------
    
    def left_up(self):
        """
        左侧升高床
        
        Returns:
            bool: 命令是否已发送
        """
        logger.info("发送左侧上升命令 LEFT_UP")
        return self.send_command("LEFT_UP")
    
    def left_down(self):
        """
        左侧降低床
        
        Returns:
            bool: 命令是否已发送
        """
        logger.info("发送左侧下降命令 LEFT_DOWN")
        return self.send_command("LEFT_DOWN")
    
    def left_stop(self):
        """
        左侧停止移动
        
        Returns:
            bool: 命令是否已发送
        """
        logger.info("发送左侧停止命令 LEFT_STOP")
        return self.send_command("LEFT_STOP")
    
    # --------- 右侧控制方法 ---------
    
    def right_up(self):
        """
        右侧升高床
        
        Returns:
            bool: 命令是否已发送
        """
        logger.info("发送右侧上升命令 RIGHT_UP")
        return self.send_command("RIGHT_UP")
    
    def right_down(self):
        """
        右侧降低床
        
        Returns:
            bool: 命令是否已发送
        """
        logger.info("发送右侧下降命令 RIGHT_DOWN")
        return self.send_command("RIGHT_DOWN")
    
    def right_stop(self):
        """
        右侧停止移动
        
        Returns:
            bool: 命令是否已发送
        """
        logger.info("发送右侧停止命令 RIGHT_STOP")
        return self.send_command("RIGHT_STOP")
    
    # --------- 状态方法 ---------
    
    def get_last_response(self):
        """获取最后一次Arduino响应"""
        return self.last_bed_response

    def get_bed_status(self):
        """
        获取床体当前状态
        
        Returns:
            dict: 包含左右侧状态的字典
        """
        return {
            "left": self.left_status,
            "right": self.right_status
        }
    
    def get_bed_height(self):
        """
        获取床体当前高度（为兼容旧API保留）
        
        Returns:
            dict: 包含床体状态信息的字典
        """
        logger.debug("获取床体状态")
        # 发送GET_STATUS命令获取最新状态
        self.send_command("GET_STATUS")
        return self.get_bed_status() 