#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
直接测试Arduino通信的脚本
发送简单命令并检查响应
"""

import serial
import time
import sys
import argparse

def parse_args():
    parser = argparse.ArgumentParser(description='Arduino通信测试')
    parser.add_argument('--port', type=str, default='/dev/ttyACM0', 
                        help='Arduino串口设备 (Raspberry Pi上通常是/dev/ttyACM0，macOS上可能是/dev/tty.usbmodem*)')
    parser.add_argument('--baud', type=int, default=9600, help='波特率')
    parser.add_argument('--debug', action='store_true', help='显示调试信息')
    return parser.parse_args()

def main():
    args = parse_args()
    
    print(f"尝试连接到 {args.port} (波特率: {args.baud})...")
    
    try:
        # 打开串口连接
        ser = serial.Serial(
            port=args.port,
            baudrate=args.baud,
            timeout=1  # 读取超时1秒
        )
        
        # 等待Arduino重置（打开串口会导致Arduino重置）
        print("等待Arduino重置和初始化...")
        time.sleep(2)
        
        # 清空任何可能在缓冲区中的数据
        ser.flushInput()
        
        print("连接成功！开始测试命令...")
        print("-" * 50)
        
        # 定义测试命令列表
        commands = [
            "UP",
            "DOWN",
            "STOP",
            "GET_HEART_RATE",
            "GET_STATUS",
            "INVALID_COMMAND"  # 测试未知命令处理
        ]
        
        # 测试每个命令
        for cmd in commands:
            print(f"\n发送命令: '{cmd}'")
            
            # 确保命令以换行符结束
            if not cmd.endswith('\n'):
                cmd_to_send = cmd + '\n'
            else:
                cmd_to_send = cmd
                
            # 发送命令
            ser.write(cmd_to_send.encode('utf-8'))
            
            # 调试信息：显示发送的原始字节
            if args.debug:
                print(f"发送字节: {[b for b in cmd_to_send.encode('utf-8')]}")
            
            # 等待并读取响应
            print("等待响应...")
            timeout_start = time.time()
            response_received = False
            
            # 尝试读取响应，最多等待3秒
            while time.time() - timeout_start < 3:
                if ser.in_waiting > 0:
                    response = ser.readline().decode('utf-8').strip()
                    print(f"收到响应: '{response}'")
                    response_received = True
                    break
                time.sleep(0.1)
            
            if not response_received:
                print("未收到响应（超时）")
            
            # 在命令之间等待一小段时间
            time.sleep(0.5)
        
        print("\n测试完成！")
        
        # 关闭连接
        ser.close()
        print("串口连接已关闭")
        
    except serial.SerialException as e:
        print(f"串口连接错误: {e}")
        return 1
    except KeyboardInterrupt:
        print("\n用户中断，正在关闭连接...")
        try:
            ser.close()
        except:
            pass
        return 0
    except Exception as e:
        print(f"发生意外错误: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 