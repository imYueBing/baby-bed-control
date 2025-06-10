#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
自动人脸跟踪模块 - 通过控制床体位置自动调整以识别人脸
"""

import logging
import threading
import time
import cv2
import numpy as np

# 配置日志
logger = logging.getLogger(__name__)

class AutoFaceTracker:
    """
    自动人脸跟踪类，通过控制床体位置自动调整以识别人脸
    """
    
    def __init__(self, camera_manager, arduino_controller, 
                 scan_interval=3.0, 
                 movement_delay=2.0,
                 face_detection_threshold=3,
                 adjustment_sequence=None):
        """
        初始化自动人脸跟踪器
        
        Args:
            camera_manager: 摄像头管理器实例
            arduino_controller: Arduino控制器实例
            scan_interval (float): 扫描间隔时间（秒）
            movement_delay (float): 移动后等待时间（秒）
            face_detection_threshold (int): 连续多少次未检测到人脸才触发调整
            adjustment_sequence (list): 自定义调整序列，如果为None则使用默认序列
        """
        self.camera_manager = camera_manager
        self.arduino_controller = arduino_controller
        self.scan_interval = scan_interval
        self.movement_delay = movement_delay
        self.face_detection_threshold = face_detection_threshold
        
        # 调整序列：每个元素是一个字典，包含动作和持续时间
        self.adjustment_sequence = adjustment_sequence or [
            {"action": "left_up", "duration": 1.0},
            {"action": "stop", "duration": 0.5},
            {"action": "right_up", "duration": 1.0},
            {"action": "stop", "duration": 0.5},
            {"action": "left_down", "duration": 1.0},
            {"action": "stop", "duration": 0.5},
            {"action": "right_down", "duration": 1.0},
            {"action": "stop", "duration": 0.5},
            {"action": "up", "duration": 1.0},
            {"action": "stop", "duration": 0.5},
            {"action": "down", "duration": 1.0},
            {"action": "stop", "duration": 0.5}
        ]
        
        self.is_running = False
        self.tracker_thread = None
        self.current_sequence_index = 0
        self.no_face_count = 0
        self.last_face_detected = False
        
    def start(self):
        """启动自动人脸跟踪"""
        if self.is_running:
            logger.warning("自动人脸跟踪已经在运行")
            return False
        
        if not self.camera_manager or not self.camera_manager.is_running:
            logger.error("摄像头未初始化或未运行")
            return False
        
        if not self.arduino_controller or not self.arduino_controller.is_connected:
            logger.error("Arduino控制器未初始化或未连接")
            return False
        
        self.is_running = True
        self.tracker_thread = threading.Thread(target=self._tracking_loop)
        self.tracker_thread.daemon = True
        self.tracker_thread.start()
        
        logger.info("自动人脸跟踪已启动")
        return True
    
    def stop(self):
        """停止自动人脸跟踪"""
        if not self.is_running:
            return
        
        self.is_running = False
        if self.tracker_thread and self.tracker_thread.is_alive():
            self.tracker_thread.join(timeout=2)
        
        # 停止所有床体移动
        if self.arduino_controller and self.arduino_controller.is_connected:
            self.arduino_controller.bed_stop()
        
        logger.info("自动人脸跟踪已停止")
    
    def _tracking_loop(self):
        """人脸跟踪主循环"""
        logger.info("人脸跟踪循环已启动")
        
        while self.is_running:
            try:
                # 获取当前帧并检测人脸
                frame = self.camera_manager.get_frame()
                faces_detected = self._detect_faces(frame)
                
                if faces_detected:
                    # 检测到人脸，重置计数器
                    self.no_face_count = 0
                    if not self.last_face_detected:
                        logger.info("检测到人脸")
                        self.last_face_detected = True
                else:
                    # 未检测到人脸，增加计数器
                    self.no_face_count += 1
                    if self.last_face_detected:
                        logger.info("未检测到人脸")
                        self.last_face_detected = False
                
                # 如果连续多次未检测到人脸，开始调整床体位置
                if self.no_face_count >= self.face_detection_threshold:
                    logger.info(f"连续 {self.no_face_count} 次未检测到人脸，开始调整床体位置")
                    self._adjust_bed_position()
                    # 重置计数器
                    self.no_face_count = 0
                
                # 等待下一次扫描
                time.sleep(self.scan_interval)
                
            except Exception as e:
                logger.error(f"人脸跟踪循环出错: {e}")
                time.sleep(1)
    
    def _detect_faces(self, frame):
        """
        检测帧中的人脸
        
        Args:
            frame: BGR格式的视频帧
            
        Returns:
            bool: 是否检测到人脸
        """
        if frame is None:
            return False
        
        # 如果摄像头已经启用了AI人脸检测，我们可以通过分析帧中的绿色矩形来判断
        # 这是一种简单的方法，假设AI人脸检测会在检测到的人脸周围绘制绿色矩形
        if self.camera_manager.enable_ai_face_detection:
            # 提取绿色通道
            green_channel = frame[:, :, 1].copy()
            
            # 阈值处理，提取亮绿色区域
            _, thresh = cv2.threshold(green_channel, 200, 255, cv2.THRESH_BINARY)
            
            # 查找轮廓
            contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # 如果找到的轮廓面积足够大，可能是人脸周围的绿色矩形
            for contour in contours:
                area = cv2.contourArea(contour)
                if area > 100:  # 面积阈值，可以根据实际情况调整
                    return True
            
            return False
        else:
            # 如果未启用AI人脸检测，使用OpenCV的Haar级联分类器
            try:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
                faces = face_cascade.detectMultiScale(gray, 1.1, 5)
                return len(faces) > 0
            except Exception as e:
                logger.error(f"人脸检测出错: {e}")
                return False
    
    def _adjust_bed_position(self):
        """调整床体位置以寻找人脸"""
        logger.info("开始调整床体位置")
        
        # 获取当前序列中的动作
        action_info = self.adjustment_sequence[self.current_sequence_index]
        action = action_info["action"]
        duration = action_info["duration"]
        
        # 执行动作
        logger.info(f"执行动作: {action}, 持续时间: {duration}秒")
        self._execute_bed_action(action)
        
        # 等待指定的持续时间
        time.sleep(duration)
        
        # 如果动作不是停止，则停止床体移动
        if action != "stop":
            logger.info("停止床体移动")
            self.arduino_controller.bed_stop()
        
        # 等待床体稳定
        time.sleep(self.movement_delay)
        
        # 更新序列索引
        self.current_sequence_index = (self.current_sequence_index + 1) % len(self.adjustment_sequence)
    
    def _execute_bed_action(self, action):
        """
        执行床体动作
        
        Args:
            action (str): 动作名称
        """
        if not self.arduino_controller or not self.arduino_controller.is_connected:
            logger.warning("Arduino控制器未初始化或未连接，无法执行动作")
            return
        
        action_methods = {
            "up": self.arduino_controller.bed_up,
            "down": self.arduino_controller.bed_down,
            "stop": self.arduino_controller.bed_stop,
            "left_up": self.arduino_controller.left_up,
            "left_down": self.arduino_controller.left_down,
            "left_stop": self.arduino_controller.left_stop,
            "right_up": self.arduino_controller.right_up,
            "right_down": self.arduino_controller.right_down,
            "right_stop": self.arduino_controller.right_stop
        }
        
        if action in action_methods:
            try:
                action_methods[action]()
                logger.info(f"执行床体动作: {action}")
            except Exception as e:
                logger.error(f"执行床体动作 {action} 时出错: {e}")
        else:
            logger.warning(f"未知的床体动作: {action}") 