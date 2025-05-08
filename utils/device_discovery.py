#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
设备发现工具 - 帮助发现连接到树莓派的Arduino设备
"""

import logging
import os
import glob
import serial
import time
import json

# 配置日志
logger = logging.getLogger(__name__)

def find_arduino_ports():
    """
    查找可能的Arduino串行端口
    
    Returns:
        list: 可能的Arduino串行端口列表
    """
    # 不同平台的串行设备路径模式
    if os.name == 'nt':  # Windows
        ports = ['COM%s' % (i + 1) for i in range(256)]
    else:  # Linux/Mac
        ports = glob.glob('/dev/tty[A-Za-z]*')
    
    # Arduino通常使用这些设备名称
    arduino_patterns = [
        'ttyUSB', 'ttyACM', 'cu.usbmodem', 'cu.usbserial'
    ]
    
    # 过滤可能的Arduino设备
    result = []
    for port in ports:
        for pattern in arduino_patterns:
            if pattern in port:
                result.append(port)
                break
    
    return result

def test_arduino_port(port, baud_rate=9600, timeout=2):
    """
    测试端口是否为有效的Arduino设备
    
    Args:
        port (str): 要测试的串行端口
        baud_rate (int): 波特率
        timeout (float): 读取超时（秒）
        
    Returns:
        bool: 端口是否为有效的Arduino设备
    """
    try:
        # 尝试打开串行端口
        ser = serial.Serial(port, baud_rate, timeout=timeout)
        
        # 等待Arduino重置
        time.sleep(2)
        
        # 刷新输入缓冲区
        ser.flushInput()
        
        # 发送系统状态请求
        command = json.dumps({'command': 'SYSTEM_STATUS'})
        ser.write(f"{command}\n".encode('utf-8'))
        
        # 读取响应
        start_time = time.time()
        while time.time() - start_time < timeout:
            if ser.in_waiting > 0:
                response = ser.readline().decode('utf-8').strip()
                try:
                    data = json.loads(response)
                    # 如果响应包含类型字段，则认为是有效的Arduino设备
                    if 'type' in data:
                        ser.close()
                        return True
                except json.JSONDecodeError:
                    # 忽略非JSON响应
                    pass
            
            time.sleep(0.1)
        
        # 超时，关闭端口
        ser.close()
        return False
        
    except (serial.SerialException, OSError) as e:
        logger.debug(f"测试端口 {port} 时出错: {e}")
        return False

def discover_arduino_device(baud_rate=9600):
    """
    自动发现并测试连接的Arduino设备
    
    Args:
        baud_rate (int): 波特率
        
    Returns:
        str or None: 找到的有效Arduino端口，如果未找到则为None
    """
    logger.info("正在搜索Arduino设备...")
    
    # 获取可能的端口
    possible_ports = find_arduino_ports()
    logger.info(f"发现 {len(possible_ports)} 个可能的串行端口: {possible_ports}")
    
    # 测试每个端口
    for port in possible_ports:
        logger.info(f"测试端口 {port}...")
        if test_arduino_port(port, baud_rate):
            logger.info(f"在端口 {port} 上找到有效的Arduino设备")
            return port
    
    logger.warning("未找到有效的Arduino设备")
    return None

if __name__ == "__main__":
    # 如果作为独立脚本运行，进行设备发现
    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # 发现设备
    port = discover_arduino_device()
    if port:
        print(f"找到Arduino设备: {port}")
    else:
        print("未找到Arduino设备") 