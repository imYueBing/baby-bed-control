#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Arduino心率通信测试脚本 - 直接与Arduino通信测试心率功能
"""

import serial
import time
import sys
import argparse
import re

def parse_args():
    parser = argparse.ArgumentParser(description='Arduino心率通信测试')
    parser.add_argument('--port', type=str, default='/dev/ttyACM0', 
                      help='Arduino串口设备 (Raspberry Pi上通常是/dev/ttyACM0，macOS上可能是/dev/tty.usbmodem*)')
    parser.add_argument('--baud', type=int, default=9600, help='波特率')
    parser.add_argument('--timeout', type=float, default=2.0, help='读取超时（秒）')
    parser.add_argument('--iterations', type=int, default=5, help='测试迭代次数')
    parser.add_argument('--interval', type=float, default=1.0, help='测试间隔（秒）')
    parser.add_argument('--debug', action='store_true', help='显示调试信息')
    return parser.parse_args()

def send_command(ser, command, debug=False):
    """发送命令到Arduino并打印调试信息"""
    # 确保命令以换行符结尾
    if not command.endswith('\n'):
        command += '\n'
    
    # 发送命令
    ser.write(command.encode('utf-8'))
    
    if debug:
        print(f"发送命令: '{command.strip()}'")
        print(f"发送字节: {[b for b in command.encode('utf-8')]}")
    else:
        print(f"发送命令: '{command.strip()}'")

def read_responses(ser, timeout=2.0, debug=False):
    """读取所有响应，直到超时"""
    responses = []
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        if ser.in_waiting > 0:
            try:
                line = ser.readline().decode('utf-8').strip()
                if line:
                    responses.append(line)
                    if debug:
                        print(f"接收到: '{line}'")
                        print(f"接收字节: {[b for b in line.encode('utf-8')]}")
                    else:
                        print(f"接收到: '{line}'")
            except UnicodeDecodeError:
                # 如果解码失败，以十六进制显示原始字节
                raw_data = ser.readline()
                hex_data = ' '.join([f'{b:02x}' for b in raw_data])
                print(f"接收到无法解码的数据: {hex_data}")
                responses.append(f"HEX:{hex_data}")
        
        # 短暂暂停，避免CPU使用率过高
        time.sleep(0.01)
    
    return responses

def extract_heart_rate(responses):
    """从响应中提取心率值"""
    for response in responses:
        # 检查各种可能的心率格式
        
        # 格式1: HEART_RATE_DATA:123
        if response.startswith("HEART_RATE_DATA:"):
            try:
                return int(response.split(":")[1].strip())
            except (IndexError, ValueError):
                pass
        
        # 格式2: [BPM] 123
        bpm_match = re.search(r'\[BPM\]\s*(\d+)', response)
        if bpm_match:
            try:
                return int(bpm_match.group(1))
            except ValueError:
                pass
                
        # 格式3: [HEART] 123
        heart_match = re.search(r'\[HEART\]\s*(\d+)', response)
        if heart_match:
            try:
                return int(heart_match.group(1))
            except ValueError:
                pass
        
        # 格式4: STATUS:BED_UP=0,BED_DOWN=0,HEART_RATE=123
        heart_rate_match = re.search(r'HEART_RATE=(\d+)', response)
        if heart_rate_match:
            try:
                return int(heart_rate_match.group(1))
            except ValueError:
                pass
                
        # 格式5: [STATUS] L_UP=0, R_UP=0, HEART=123
        heart_status_match = re.search(r'HEART=(\d+)', response)
        if heart_status_match:
            try:
                return int(heart_status_match.group(1))
            except ValueError:
                pass
    
    return None

def main():
    args = parse_args()
    
    print(f"=== Arduino心率通信测试 ===")
    print(f"端口: {args.port}")
    print(f"波特率: {args.baud}")
    print(f"超时: {args.timeout}秒")
    print(f"迭代次数: {args.iterations}")
    print(f"测试间隔: {args.interval}秒")
    print(f"调试模式: {'开启' if args.debug else '关闭'}")
    print("=" * 30)
    
    try:
        # 打开串口连接
        print(f"尝试连接到 {args.port}...")
        ser = serial.Serial(
            port=args.port,
            baudrate=args.baud,
            timeout=args.timeout
        )
        
        # 等待Arduino重置（打开串口会导致Arduino重置）
        print("等待Arduino重置和初始化...")
        time.sleep(2)
        
        # 清空接收缓冲区
        ser.flushInput()
        
        print(f"连接成功! 开始测试心率功能...")
        
        # 测试发送GET_HEART_RATE命令
        success_count = 0
        heart_rates = []
        
        for i in range(args.iterations):
            print(f"\n--- 测试 {i+1}/{args.iterations} ---")
            
            # 发送命令
            send_command(ser, "GET_HEART_RATE", args.debug)
            
            # 读取响应
            print("等待响应...")
            responses = read_responses(ser, args.timeout, args.debug)
            
            # 检查是否收到响应
            if responses:
                print(f"收到 {len(responses)} 个响应")
                
                # 尝试提取心率值
                heart_rate = extract_heart_rate(responses)
                if heart_rate is not None:
                    print(f"成功提取心率值: {heart_rate}")
                    success_count += 1
                    heart_rates.append(heart_rate)
                else:
                    print("无法从响应中提取心率值")
            else:
                print("未收到响应")
            
            # 在测试间隔
            if i < args.iterations - 1:
                time.sleep(args.interval)
        
        # 测试GET_STATUS命令
        print("\n--- 测试 GET_STATUS 命令 ---")
        send_command(ser, "GET_STATUS", args.debug)
        status_responses = read_responses(ser, args.timeout, args.debug)
        status_heart_rate = extract_heart_rate(status_responses)
        
        if status_heart_rate is not None:
            print(f"从状态响应中提取的心率值: {status_heart_rate}")
        else:
            print("无法从状态响应中提取心率值")
        
        # 打印测试结果
        print("\n=== 测试结果 ===")
        print(f"成功率: {success_count}/{args.iterations} ({success_count/args.iterations*100:.1f}%)")
        
        if heart_rates:
            print(f"心率值: {heart_rates}")
            print(f"平均心率: {sum(heart_rates)/len(heart_rates):.1f}")
        
        # 关闭连接
        ser.close()
        print("串口连接已关闭")
        
        return 0 if success_count > 0 else 1
        
    except serial.SerialException as e:
        print(f"串口错误: {e}")
        return 1
    except KeyboardInterrupt:
        print("\n用户中断，退出测试")
        try:
            ser.close()
        except:
            pass
        return 0
    except Exception as e:
        print(f"发生意外错误: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 