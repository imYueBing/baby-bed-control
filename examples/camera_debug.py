#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
摄像头调试示例 - 在本地显示摄像头捕获的画面
"""

import sys
import os
import time
import signal
import logging

# 确保可以导入项目模块
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

from modules.camera import CameraManager

def signal_handler(sig, frame):
    """处理 Ctrl+C 信号"""
    print('\n正在停止...')
    if camera:
        camera.close()
    sys.exit(0)

if __name__ == "__main__":
    # 注册信号处理
    signal.signal(signal.SIGINT, signal_handler)
    
    # 创建相机管理器实例
    camera = CameraManager(
        resolution=(800, 600),  # 更高的分辨率以便更好地查看
        framerate=30,
        use_picamera=True  # 使用树莓派相机
    )
    
    # 启动本地调试窗口
    camera.start_debug_window(window_name="Raspberry Pi Camera Module 3")
    
    print("摄像头调试窗口已启动")
    print("按ESC键或Ctrl+C退出")
    
    try:
        # 保持程序运行直到用户停止
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        # 确保正确关闭相机
        if camera:
            camera.stop_debug_window()
            camera.close()
            print("已关闭摄像头") 