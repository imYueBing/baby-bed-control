#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
日志工具模块 - 提供统一的日志配置
"""

import logging
import os
import sys
from datetime import datetime

def setup_logger(name='baby_monitor', level=logging.INFO, log_dir='logs'):
    """
    配置日志记录器
    
    Args:
        name (str): 日志记录器名称
        level (int): 日志级别
        log_dir (str): 日志目录
        
    Returns:
        logging.Logger: 配置好的日志记录器
    """
    # 创建日志目录
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # 生成日志文件名
    timestamp = datetime.now().strftime("%Y%m%d")
    log_file = os.path.join(log_dir, f"{name}_{timestamp}.log")
    
    # 获取记录器
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # 如果已经有处理程序，直接返回
    if logger.handlers:
        return logger
    
    # 创建控制台处理程序
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    
    # 创建文件处理程序
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(level)
    
    # 创建格式器
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # 添加格式器到处理程序
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)
    
    # 添加处理程序到记录器
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    logger.info(f"日志记录器已配置，日志文件: {log_file}")
    
    return logger

def get_logger(name='baby_monitor'):
    """
    获取已配置的日志记录器，如果不存在则创建
    
    Args:
        name (str): 日志记录器名称
        
    Returns:
        logging.Logger: 日志记录器
    """
    logger = logging.getLogger(name)
    
    # 如果没有处理程序，进行配置
    if not logger.handlers:
        # 获取环境变量中的日志级别，默认为INFO
        level_name = os.environ.get('LOG_LEVEL', 'INFO')
        level = getattr(logging, level_name.upper(), logging.INFO)
        
        # 获取环境变量中的日志目录，默认为'logs'
        log_dir = os.environ.get('LOG_DIR', 'logs')
        
        return setup_logger(name, level, log_dir)
    
    return logger 