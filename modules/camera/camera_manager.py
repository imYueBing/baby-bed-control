#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
摄像头管理模块 - 负责视频捕获和流处理
"""

import cv2
import logging
import threading
import time
import numpy as np
from datetime import datetime
import os

# 配置日志
logger = logging.getLogger(__name__)

class CameraManager:
    """摄像头管理类，负责视频捕获和处理"""
    
    def __init__(self, resolution=(640, 480), framerate=30, use_picamera=True):
        """
        初始化摄像头管理器
        
        Args:
            resolution (tuple): 分辨率 (宽, 高)
            framerate (int): 帧率
            use_picamera (bool): 是否使用树莓派摄像头
        """
        self.resolution = resolution
        self.framerate = framerate
        self.use_picamera = use_picamera
        self.camera = None
        self.is_running = False
        self.is_recording = False
        self.recording_thread = None
        self.current_frame = None
        self.frame_lock = threading.Lock()
        self.frame_available = threading.Event()
        self.clients = []
        self.clients_lock = threading.Lock()
        
        # 初始化摄像头
        self._init_camera()
    
    def _init_camera(self):
        """初始化摄像头"""
        try:
            # 尝试使用PiCamera库（如果可用且启用）
            if self.use_picamera:
                try:
                    from picamera2 import Picamera2
                    self.camera = Picamera2()
                    config = self.camera.create_video_configuration(
                        main={"size": self.resolution, "format": "RGB888"},
                        controls={"FrameRate": self.framerate}
                    )
                    self.camera.configure(config)
                    self.camera.start()
                    logger.info("已初始化树莓派摄像头")
                except (ImportError, ModuleNotFoundError):
                    logger.warning("无法导入picamera2模块，回退到OpenCV")
                    self.use_picamera = False
            
            # 如果不使用PiCamera或者导入失败，使用OpenCV
            if not self.use_picamera:
                self.camera = cv2.VideoCapture(0)
                self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, self.resolution[0])
                self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, self.resolution[1])
                self.camera.set(cv2.CAP_PROP_FPS, self.framerate)
                
                if not self.camera.isOpened():
                    raise RuntimeError("无法打开摄像头")
                
                logger.info("已初始化OpenCV摄像头")
            
            # 启动捕获线程
            self.is_running = True
            self.capture_thread = threading.Thread(target=self._capture_loop)
            self.capture_thread.daemon = True
            self.capture_thread.start()
            
        except Exception as e:
            logger.error(f"初始化摄像头失败: {e}")
            self.camera = None
    
    def _capture_loop(self):
        """捕获视频帧的循环"""
        while self.is_running and self.camera:
            try:
                # 获取帧
                if self.use_picamera:
                    # 使用PiCamera API
                    frame = self.camera.capture_array()
                    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                    success = True
                else:
                    # 使用OpenCV
                    success, frame = self.camera.read()
                
                if success:
                    # 在帧上添加时间戳
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    cv2.putText(
                        frame, 
                        timestamp, 
                        (10, frame.shape[0] - 10), 
                        cv2.FONT_HERSHEY_SIMPLEX, 
                        0.5, 
                        (255, 255, 255), 
                        1, 
                        cv2.LINE_AA
                    )
                    
                    # 更新当前帧
                    with self.frame_lock:
                        self.current_frame = frame.copy()
                    
                    # 设置帧可用事件
                    self.frame_available.set()
                    
                    # 通知所有客户端
                    self._notify_clients()
                
                # 等待适当的时间以保持帧率
                time.sleep(1.0 / self.framerate)
                
            except Exception as e:
                logger.error(f"捕获视频帧时出错: {e}")
                time.sleep(1)  # 错误后暂停
    
    def _notify_clients(self):
        """通知所有注册的客户端有新帧可用"""
        with self.clients_lock:
            # 创建客户端列表的副本以避免在迭代过程中修改
            clients_copy = self.clients.copy()
        
        for callback in clients_copy:
            try:
                callback(self.get_frame())
            except Exception as e:
                logger.error(f"通知客户端时出错: {e}")
                # 如果回调失败，移除该客户端
                with self.clients_lock:
                    if callback in self.clients:
                        self.clients.remove(callback)
    
    def close(self):
        """关闭摄像头并清理资源"""
        self.is_running = False
        self.stop_recording()
        
        if self.capture_thread and self.capture_thread.is_alive():
            self.capture_thread.join(timeout=2)
        
        if self.camera:
            if self.use_picamera:
                self.camera.stop()
                self.camera.close()
            else:
                self.camera.release()
            
            self.camera = None
            logger.info("摄像头已关闭")
    
    def get_frame(self):
        """
        获取当前视频帧
        
        Returns:
            numpy.ndarray: BGR格式的视频帧
        """
        if not self.is_running or self.current_frame is None:
            # 返回一个黑色图像
            black_frame = np.zeros((480, 640, 3), dtype=np.uint8)
            cv2.putText(
                black_frame, 
                "Camera Unavailable", 
                (180, 240), 
                cv2.FONT_HERSHEY_SIMPLEX, 
                1, 
                (255, 255, 255), 
                2, 
                cv2.LINE_AA
            )
            return black_frame
        
        # 等待帧可用
        self.frame_available.wait(timeout=1.0)
        
        # 获取当前帧的副本
        with self.frame_lock:
            if self.current_frame is not None:
                return self.current_frame.copy()
            else:
                return np.zeros((480, 640, 3), dtype=np.uint8)
    
    def get_jpeg_frame(self, quality=90):
        """
        获取JPEG编码的当前帧
        
        Args:
            quality (int): JPEG质量，范围0-100
            
        Returns:
            bytes: JPEG编码的视频帧
        """
        frame = self.get_frame()
        ret, jpeg = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, quality])
        if ret:
            return jpeg.tobytes()
        return None
    
    def register_client(self, callback):
        """
        注册一个视频帧客户端
        
        Args:
            callback (callable): 当新帧可用时调用的回调函数
        """
        with self.clients_lock:
            if callback not in self.clients:
                self.clients.append(callback)
    
    def unregister_client(self, callback):
        """
        注销一个视频帧客户端
        
        Args:
            callback (callable): 先前注册的回调函数
        """
        with self.clients_lock:
            if callback in self.clients:
                self.clients.remove(callback)
    
    def start_recording(self, output_path="videos"):
        """
        开始录制视频
        
        Args:
            output_path (str): 输出目录路径
        """
        if self.is_recording:
            logger.warning("已经在录制视频")
            return False
        
        # 创建输出目录
        os.makedirs(output_path, exist_ok=True)
        
        # 创建输出文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.video_file = os.path.join(output_path, f"video_{timestamp}.mp4")
        
        # 创建视频写入器
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        self.video_writer = cv2.VideoWriter(
            self.video_file,
            fourcc,
            self.framerate,
            self.resolution
        )
        
        if not self.video_writer.isOpened():
            logger.error("无法创建视频写入器")
            return False
        
        # 开始录制线程
        self.is_recording = True
        self.recording_thread = threading.Thread(target=self._recording_loop)
        self.recording_thread.daemon = True
        self.recording_thread.start()
        
        logger.info(f"开始录制视频: {self.video_file}")
        return True
    
    def stop_recording(self):
        """停止录制视频"""
        if not self.is_recording:
            return
        
        self.is_recording = False
        
        if self.recording_thread and self.recording_thread.is_alive():
            self.recording_thread.join(timeout=2)
        
        if hasattr(self, 'video_writer') and self.video_writer:
            self.video_writer.release()
            logger.info(f"视频已保存: {self.video_file}")
    
    def _recording_loop(self):
        """视频录制循环"""
        while self.is_recording and self.video_writer:
            try:
                # 获取当前帧
                frame = self.get_frame()
                
                # 写入帧
                self.video_writer.write(frame)
                
                # 等待下一帧
                time.sleep(1.0 / self.framerate)
                
            except Exception as e:
                logger.error(f"录制视频时出错: {e}")
                self.is_recording = False
                break 