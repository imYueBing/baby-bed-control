#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
功能模块包初始化文件

提供所有模块的导出
"""

# 导出Arduino控制器相关模块
from .arduino import ArduinoController, BaseArduinoController, BedController, HeartRateController

# 导出相机管理器模块
try:
    from .camera import CameraManager
except ImportError:
    # 如果相机模块不可用（例如，在非树莓派上运行），提供可用性标志
    CameraManager = None
    HAS_CAMERA = False
else:
    HAS_CAMERA = True

__all__ = [
    'ArduinoController',
    'BaseArduinoController',
    'BedController',
    'HeartRateController',
    'CameraManager',
    'HAS_CAMERA'
] 