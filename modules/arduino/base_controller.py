#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Arduino基础控制器模块 - 负责与Arduino的基本串行通信
"""

import json
import logging
import queue
import serial
import threading
import time

# 配置日志
logger = logging.getLogger(__name__)

class BaseArduinoController:
    """Arduino基础控制器类，处理基本的串行通信"""
    
    def __init__(self, port, baud_rate=9600, timeout=1):
        """
        初始化Arduino基础控制器
        
        Args:
            port (str): 串行端口（例如 '/dev/ttyUSB0'）
            baud_rate (int): 波特率
            timeout (float): 读取超时（秒）
        """
        self.port = port
        self.baud_rate = baud_rate
        self.timeout = timeout
        self.serial = None
        self.is_connected = False
        self.read_thread = None
        self.running = False
        
        # 命令队列
        self.command_queue = queue.Queue()
        
        # 尝试连接
        self._connect()
    
    def _connect(self):
        """尝试连接到Arduino"""
        try:
            self.serial = serial.Serial(
                port=self.port,
                baudrate=self.baud_rate,
                timeout=self.timeout
            )
            
            # 等待Arduino重置
            time.sleep(2)
            
            # 刷新输入缓冲区
            self.serial.flushInput()
            
            logger.info(f"已连接到Arduino: {self.port}")
            self.is_connected = True
            
            # 启动读取线程
            self.running = True
            self.read_thread = threading.Thread(target=self._read_loop)
            self.read_thread.daemon = True
            self.read_thread.start()
            
            # 启动命令处理线程
            self.command_thread = threading.Thread(target=self._command_loop)
            self.command_thread.daemon = True
            self.command_thread.start()
            
            # 请求系统状态
            self.get_system_status()
            
        except serial.SerialException as e:
            logger.error(f"无法连接到Arduino: {e}")
            self.is_connected = False
    
    def reconnect(self):
        """重新连接到Arduino"""
        if self.is_connected:
            self.close()
        self._connect()
    
    def close(self):
        """关闭连接"""
        self.running = False
        
        if self.read_thread:
            if self.read_thread.is_alive():
                self.read_thread.join(timeout=1)
        
        if self.command_thread:
            if self.command_thread.is_alive():
                self.command_thread.join(timeout=1)
        
        if self.serial and self.serial.is_open:
            self.serial.close()
            logger.info("Arduino连接已关闭")
        
        self.is_connected = False
    
    def _read_loop(self):
        """从Arduino读取数据的循环"""
        while self.running and self.serial and self.serial.is_open:
            try:
                if self.serial.in_waiting > 0:
                    line = self.serial.readline().decode('utf-8').strip()
                    if line:
                        self._process_response(line)
            except serial.SerialException as e:
                logger.error(f"串行读取错误: {e}")
                self.is_connected = False
                break
            except Exception as e:
                logger.error(f"读取循环中的错误: {e}")
            
            # 短暂暂停，避免CPU占用过高
            time.sleep(0.01)
    
    def _command_loop(self):
        """命令处理循环"""
        while self.running and self.serial and self.serial.is_open:
            try:
                # 从队列获取命令（阻塞，等待1秒）
                try:
                    command = self.command_queue.get(timeout=1)
                except queue.Empty:
                    continue
                
                # 发送命令
                if self.serial and self.serial.is_open:
                    self.serial.write(f"{command}\n".encode('utf-8'))
                    logger.debug(f"发送命令: {command}")
                
                # 标记任务完成
                self.command_queue.task_done()
                
                # 短暂等待，避免命令发送过快
                time.sleep(0.1)
                
            except serial.SerialException as e:
                logger.error(f"串行写入错误: {e}")
                self.is_connected = False
                break
            except Exception as e:
                logger.error(f"命令循环中的错误: {e}")
    
    def _process_response(self, response):
        """
        处理来自Arduino的响应
        子类应重写此方法以处理特定响应
        """
        try:
            # 尝试解析为JSON
            data = json.loads(response)
            logger.debug(f"收到响应: {data}")
            
            # 具体的响应处理由子类实现
            self._handle_response(data)
            
        except json.JSONDecodeError:
            # 非JSON响应
            logger.debug(f"收到非JSON响应: {response}")
        
        except Exception as e:
            logger.error(f"处理响应时出错: {e}")
    
    def _handle_response(self, data):
        """
        处理特定类型的响应
        应由子类重写
        
        Args:
            data (dict): 解析后的JSON响应
        """
        pass
    
    def send_command(self, command_type, **kwargs):
        """
        发送命令到Arduino
        
        Args:
            command_type (str): 命令类型
            **kwargs: 命令参数
        
        Returns:
            bool: 命令是否已发送
        """
        if not self.is_connected:
            logger.warning(f"Arduino未连接，无法发送命令: {command_type}")
            return False
        
        command_data = {'command': command_type}
        command_data.update(kwargs)
        
        command = json.dumps(command_data)
        self.command_queue.put(command)
        return True
    
    def get_system_status(self):
        """获取系统状态"""
        return self.send_command("SYSTEM_STATUS") 