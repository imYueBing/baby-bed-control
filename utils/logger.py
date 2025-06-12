#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Logger Utility Module - Provides unified logging configuration
"""

import logging
import os
import sys
from datetime import datetime

def setup_logger(name='baby_monitor', level=logging.INFO, log_dir='logs'):
    """
    Configure logger
    
    Args:
        name (str): Logger name
        level (int): Log level
        log_dir (str): Log directory
        
    Returns:
        logging.Logger: Configured logger
    """
    # Create log directory
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Generate log filename
    timestamp = datetime.now().strftime("%Y%m%d")
    log_file = os.path.join(log_dir, f"{name}_{timestamp}.log")
    
    # Get logger
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # If handlers already exist, return directly
    if logger.handlers:
        return logger
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    
    # Create file handler
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(level)
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Add formatter to handlers
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)
    
    # Add handlers to logger
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    logger.info(f"Logger configured, log file: {log_file}")
    
    return logger

def get_logger(name='baby_monitor'):
    """
    Get configured logger, create if it doesn't exist
    
    Args:
        name (str): Logger name
        
    Returns:
        logging.Logger: Logger
    """
    logger = logging.getLogger(name)
    
    # If no handlers, configure
    if not logger.handlers:
        # Get log level from environment variable, default to INFO
        level_name = os.environ.get('LOG_LEVEL', 'INFO')
        level = getattr(logging, level_name.upper(), logging.INFO)
        
        # Get log directory from environment variable, default to 'logs'
        log_dir = os.environ.get('LOG_DIR', 'logs')
        
        return setup_logger(name, level, log_dir)
    
    return logger 