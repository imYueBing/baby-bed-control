#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
床体控制API测试脚本 - 测试床体左右独立控制功能
"""

import requests
import json
import sys
import argparse
import time

def parse_args():
    parser = argparse.ArgumentParser(description='床体控制API测试')
    parser.add_argument('--host', type=str, default='localhost', 
                        help='API服务器主机名或IP地址')
    parser.add_argument('--port', type=int, default=5000, 
                        help='API服务器端口')
    parser.add_argument('--debug', action='store_true',
                        help='启用调试输出')
    return parser.parse_args()

def send_api_request(base_url, endpoint, method='GET', data=None, debug=False):
    """发送API请求并返回结果"""
    url = f"{base_url}{endpoint}"
    
    if debug:
        print(f"发送 {method} 请求到 {url}")
        if data:
            print(f"数据: {data}")
    
    try:
        if method.upper() == 'GET':
            response = requests.get(url, timeout=5)
        elif method.upper() == 'POST':
            response = requests.post(url, json=data, timeout=5)
        else:
            print(f"不支持的方法: {method}")
            return None
        
        if debug:
            print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"请求失败 ({response.status_code}): {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"请求错误: {e}")
        return None

def test_bed_status(base_url, debug=False):
    """测试获取床体状态"""
    print("\n=== 测试床体状态 ===")
    
    response = send_api_request(base_url, "/api/bed/status", "GET", debug=debug)
    
    if response:
        print(f"床体状态: {json.dumps(response, ensure_ascii=False, indent=2)}")
        return True
    else:
        print("获取床体状态失败")
        return False

def test_bed_controls(base_url, debug=False):
    """测试床体控制功能"""
    print("\n=== 测试床体控制 ===")
    
    # 测试整体控制
    print("\n--- 测试整体控制 ---")
    commands = [
        {"endpoint": "/api/bed/up", "name": "整体上升"},
        {"endpoint": "/api/bed/stop", "name": "整体停止"},
        {"endpoint": "/api/bed/down", "name": "整体下降"},
        {"endpoint": "/api/bed/stop", "name": "整体停止"}
    ]
    
    success_count = 0
    for cmd in commands:
        print(f"\n发送 {cmd['name']} 命令...")
        response = send_api_request(base_url, cmd["endpoint"], "POST", debug=debug)
        
        if response:
            print(f"响应: {json.dumps(response, ensure_ascii=False, indent=2)}")
            success_count += 1
        else:
            print(f"发送 {cmd['name']} 命令失败")
        
        # 短暂等待，以便看到效果
        time.sleep(1)
    
    # 获取状态
    test_bed_status(base_url, debug)
    
    # 测试左侧控制
    print("\n--- 测试左侧控制 ---")
    left_commands = [
        {"endpoint": "/api/bed/left_up", "name": "左侧上升"},
        {"endpoint": "/api/bed/left_stop", "name": "左侧停止"},
        {"endpoint": "/api/bed/left_down", "name": "左侧下降"},
        {"endpoint": "/api/bed/left_stop", "name": "左侧停止"}
    ]
    
    for cmd in left_commands:
        print(f"\n发送 {cmd['name']} 命令...")
        response = send_api_request(base_url, cmd["endpoint"], "POST", debug=debug)
        
        if response:
            print(f"响应: {json.dumps(response, ensure_ascii=False, indent=2)}")
            success_count += 1
        else:
            print(f"发送 {cmd['name']} 命令失败")
        
        # 短暂等待，以便看到效果
        time.sleep(1)
    
    # 获取状态
    test_bed_status(base_url, debug)
    
    # 测试右侧控制
    print("\n--- 测试右侧控制 ---")
    right_commands = [
        {"endpoint": "/api/bed/right_up", "name": "右侧上升"},
        {"endpoint": "/api/bed/right_stop", "name": "右侧停止"},
        {"endpoint": "/api/bed/right_down", "name": "右侧下降"},
        {"endpoint": "/api/bed/right_stop", "name": "右侧停止"}
    ]
    
    for cmd in right_commands:
        print(f"\n发送 {cmd['name']} 命令...")
        response = send_api_request(base_url, cmd["endpoint"], "POST", debug=debug)
        
        if response:
            print(f"响应: {json.dumps(response, ensure_ascii=False, indent=2)}")
            success_count += 1
        else:
            print(f"发送 {cmd['name']} 命令失败")
        
        # 短暂等待，以便看到效果
        time.sleep(1)
    
    # 获取状态
    test_bed_status(base_url, debug)
    
    total_commands = len(commands) + len(left_commands) + len(right_commands)
    print(f"\n命令测试结果: {success_count}/{total_commands} 成功")
    
    return success_count == total_commands

def main():
    args = parse_args()
    base_url = f"http://{args.host}:{args.port}"
    
    print(f"=== 床体控制API测试 ===")
    print(f"API基础URL: {base_url}")
    print(f"调试模式: {'开启' if args.debug else '关闭'}")
    print("=" * 30)
    
    # 测试床体状态
    status_ok = test_bed_status(base_url, args.debug)
    
    # 测试床体控制
    controls_ok = test_bed_controls(base_url, args.debug)
    
    # 总结
    print("\n=== 测试总结 ===")
    print(f"状态API测试: {'成功' if status_ok else '失败'}")
    print(f"控制API测试: {'成功' if controls_ok else '失败'}")
    
    return 0 if status_ok and controls_ok else 1

if __name__ == "__main__":
    sys.exit(main()) 