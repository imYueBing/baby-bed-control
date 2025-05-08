#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
婴儿监控系统 - 测试脚本
用于测试各个组件的连接和基本功能
"""

import argparse
import json
import logging
import os
import sys
import time

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("test_system")

def test_arduino():
    """测试Arduino连接和功能"""
    logger.info("===== 测试Arduino连接 =====")
    
    try:
        from utils.device_discovery import discover_arduino_device
        from modules.arduino.controller import ArduinoController
        
        # 发现Arduino设备
        port = discover_arduino_device()
        
        if not port:
            logger.error("无法找到Arduino设备")
            return False
        
        logger.info(f"找到Arduino设备: {port}")
        
        # 初始化控制器
        controller = ArduinoController(port=port)
        
        if not controller.is_connected:
            logger.error("Arduino控制器初始化失败")
            return False
        
        # 测试获取心率
        logger.info("测试获取心率...")
        heart_rate = controller.get_heart_rate()
        logger.info(f"当前心率: {heart_rate if heart_rate is not None else '未知'}")
        
        # 测试获取床体高度
        logger.info("测试获取床体高度...")
        height = controller.get_bed_height()
        logger.info(f"当前床体高度: {height if height is not None else '未知'}")
        
        # 测试床体控制
        logger.info("测试床体控制...")
        
        logger.info("升高床体 (1秒)...")
        controller.bed_up()
        time.sleep(1)
        
        logger.info("停止床体...")
        controller.bed_stop()
        time.sleep(0.5)
        
        logger.info("降低床体 (1秒)...")
        controller.bed_down()
        time.sleep(1)
        
        logger.info("停止床体...")
        controller.bed_stop()
        
        # 关闭控制器
        controller.close()
        logger.info("Arduino测试完成")
        
        return True
        
    except Exception as e:
        logger.error(f"Arduino测试失败: {e}")
        return False

def test_camera():
    """测试摄像头功能"""
    logger.info("===== 测试摄像头 =====")
    
    try:
        from modules.camera.camera_manager import CameraManager
        import cv2
        
        # 初始化摄像头
        camera = CameraManager(resolution=(640, 480), framerate=30)
        
        if not camera.is_running:
            logger.error("摄像头初始化失败")
            return False
        
        # 获取并显示帧
        for i in range(5):
            logger.info(f"获取帧 {i+1}/5...")
            frame = camera.get_frame()
            
            if frame is None:
                logger.error("无法获取视频帧")
                break
            
            # 获取帧大小
            height, width = frame.shape[:2]
            logger.info(f"帧大小: {width}x{height}")
            
            # 保存帧为JPEG
            jpg_file = f"test_frame_{i+1}.jpg"
            cv2.imwrite(jpg_file, frame)
            logger.info(f"已保存帧到 {jpg_file}")
            
            time.sleep(1)
        
        # 测试录制
        logger.info("测试视频录制 (3秒)...")
        camera.start_recording("test_videos")
        time.sleep(3)
        camera.stop_recording()
        logger.info("录制完成")
        
        # 关闭摄像头
        camera.close()
        logger.info("摄像头测试完成")
        
        return True
        
    except Exception as e:
        logger.error(f"摄像头测试失败: {e}")
        return False

def test_api_server():
    """测试API服务器"""
    logger.info("===== 测试API服务器 =====")
    
    try:
        from utils.device_discovery import discover_arduino_device
        from modules.arduino.controller import ArduinoController
        from modules.camera.camera_manager import CameraManager
        from api.server import APIServer
        
        # 发现Arduino设备
        port = discover_arduino_device()
        
        if not port:
            logger.warning("无法找到Arduino设备，将使用模拟设备")
            # 使用一个不存在的端口，让控制器进入离线模式
            port = "/dev/ttyNONEXISTENT"
        
        # 初始化组件
        arduino_controller = ArduinoController(port=port)
        camera_manager = CameraManager(resolution=(640, 480), framerate=30)
        
        # 初始化API服务器
        api_server = APIServer(
            arduino_controller=arduino_controller,
            camera_manager=camera_manager,
            host='127.0.0.1',  # 仅监听本地连接
            port=5000
        )
        
        # 启动服务器
        logger.info("启动API服务器...")
        api_server.start()
        
        # 等待服务器完全启动
        time.sleep(2)
        
        # 测试API
        import requests
        
        logger.info("测试API: GET /api/status")
        response = requests.get("http://127.0.0.1:5000/api/status")
        logger.info(f"状态码: {response.status_code}")
        logger.info(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        
        # 等待一段时间以便查看服务器日志
        logger.info("API服务器已启动并测试完成")
        logger.info("按Ctrl+C停止服务器...")
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            pass
        
        # 关闭服务器和组件
        logger.info("停止API服务器...")
        api_server.stop()
        arduino_controller.close()
        camera_manager.close()
        
        return True
        
    except Exception as e:
        logger.error(f"API服务器测试失败: {e}")
        return False

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="婴儿监控系统测试脚本")
    parser.add_argument("--arduino", action="store_true", help="测试Arduino连接")
    parser.add_argument("--camera", action="store_true", help="测试摄像头")
    parser.add_argument("--api", action="store_true", help="测试API服务器")
    parser.add_argument("--all", action="store_true", help="测试所有组件")
    
    args = parser.parse_args()
    
    # 如果没有指定参数，显示帮助
    if not (args.arduino or args.camera or args.api or args.all):
        parser.print_help()
        return
    
    # 测试Arduino
    if args.arduino or args.all:
        test_arduino()
    
    # 测试摄像头
    if args.camera or args.all:
        test_camera()
    
    # 测试API服务器
    if args.api or args.all:
        test_api_server()

if __name__ == "__main__":
    main() 