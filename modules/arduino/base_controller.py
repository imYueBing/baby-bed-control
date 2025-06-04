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
                # 尝试添加 dsrdtr=False 如果遇到连接问题
                # dsrdtr=False 
            )
            
            # 对于许多Arduino板，打开串口会导致复位。
            # 这个延迟是为了给Arduino足够的时间来完成复位并准备好接收数据。
            logger.info("等待Arduino板复位和初始化 (通常需要1-2秒)...")
            time.sleep(2) 
            
            self.serial.flushInput() # 清除任何在Python准备好之前Arduino可能发送的初始数据
            
            # 尝试读取Arduino的初始就绪消息 (可选)
            # 这有助于确认双向通信，但如果Arduino没有发送或者被flushInput清除了也不算严重错误
            try:
                initial_message = self.serial.readline().decode('utf-8').strip()
                if initial_message:
                    logger.info(f"从Arduino收到初始消息: {initial_message}")
                else:
                    logger.debug("未收到Arduino的初始就绪消息 (可能已被清除或未发送)。")
            except Exception as e:
                logger.debug(f"读取初始消息时出错 (可忽略): {e}")


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
            logger.error(f"无法连接到Arduino (端口: {self.port}, 波特率: {self.baud_rate}): 详细错误: {e}")
            self.is_connected = False
        except Exception as ex:
            logger.error(f"连接Arduino时发生意外错误 (端口: {self.port}): {ex}", exc_info=True)
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
                        logger.debug(f"从Arduino原始接收: {line}") # 添加原始数据日志
                        self._process_response(line) # 直接将原始行传递给处理函数
            except serial.SerialException as e:
                logger.error(f"串行读取错误: {e}")
                self.is_connected = False
                break
            except Exception as e:
                logger.error(f"读取循环中的错误: {e}")
            
            # 短暂暂停，避免CPU占用过高
            time.sleep(0.01)
    
    def _command_loop(self):
        """命令处理循环 - 从队列获取命令并发送"""
        while self.running and self.serial and self.serial.is_open:
            try:
                # 从队列获取命令（阻塞，等待1秒）
                try:
                    # command_to_send 现在应该是完整的字符串，包含 \\n
                    command_to_send = self.command_queue.get(timeout=1) 
                except queue.Empty:
                    continue
                
                # 发送命令
                if self.serial and self.serial.is_open:
                    self.serial.write(command_to_send.encode('utf-8')) # 直接编码发送
                    logger.debug(f"已发送命令到Arduino: {command_to_send.strip()}") # 记录剥离了换行符的命令
                
                self.command_queue.task_done()
                time.sleep(0.1) # 短暂等待，避免命令发送过快
                
            except serial.SerialException as e:
                logger.error(f"串行写入错误: {e}")
                self.is_connected = False
                break
            except Exception as e:
                logger.error(f"命令循环中的错误: {e}")
    
    def _process_response(self, response_line):
        """
        处理来自Arduino的响应 (简化为直接处理字符串)
        子类可以覆盖此方法以进行更具体的处理。
        """
        logger.info(f"Arduino响应: {response_line}")
        # 在这个简化的版本中，我们只是记录响应。
        # 在实际应用中，您会在这里解析响应并触发相应的事件或更新状态。
        # 例如，您可以检查 response_line.startswith("CONFIRMED:") 等
        
        # 为了让子控制器可以处理，我们仍然调用一个可被覆盖的方法
        self._handle_specific_response(response_line)

    def _handle_specific_response(self, response_line):
        """
        由子类实现以处理特定响应。
        """
        pass # 子类将实现这个

    def send_command(self, command_string): # 修改参数为简单字符串
        """
        发送简单的字符串命令到Arduino，并确保以换行符结束。
        
        Args:
            command_string (str): 要发送的命令字符串 (例如 "UP", "DOWN")
        
        Returns:
            bool: 命令是否已成功放入发送队列
        """
        if not self.is_connected:
            logger.warning(f"Arduino未连接，无法发送命令: {command_string}")
            return False
        
        # 确保命令以换行符结束
        if not command_string.endswith('\n'):
            command_to_send = command_string + '\n'
        else:
            command_to_send = command_string
            
        self.command_queue.put(command_to_send) # 将修改后的命令放入队列
        # 注意：_command_loop 会从队列中取出并 .encode('utf-8') 发送
        logger.debug(f"命令 '{command_string}' 已放入发送队列。")
        return True
    
    def get_system_status(self):
        """获取系统状态 (简化测试，发送一个特定命令)"""
        return self.send_command("GET_STATUS\\n") # 示例，Arduino端需要对应处理 