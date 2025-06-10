#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
前端API测试脚本 - 模拟前端请求测试API endpoints
"""

import requests
import json
import sys
import argparse
import socketio
import time

def parse_args():
    parser = argparse.ArgumentParser(description='前端API测试')
    parser.add_argument('--host', type=str, default='localhost', 
                        help='API服务器主机名或IP地址')
    parser.add_argument('--port', type=int, default=5000, 
                        help='API服务器端口')
    parser.add_argument('--test-websocket', action='store_true', 
                        help='测试WebSocket连接')
    return parser.parse_args()

def test_http_api(base_url):
    """测试HTTP API端点"""
    endpoints = [
        # 床体控制API
        {'url': '/api/bed/up', 'method': 'post', 'description': '升高床'},
        {'url': '/api/bed/down', 'method': 'post', 'description': '降低床'},
        {'url': '/api/bed/stop', 'method': 'post', 'description': '停止床体移动'},
        {'url': '/api/bed/height', 'method': 'get', 'description': '获取床体高度'},
        
        # 心率监测API
        {'url': '/api/heart-rate', 'method': 'get', 'description': '获取心率'},
        
        # 系统API
        {'url': '/api/system/status', 'method': 'get', 'description': '获取系统状态'},
    ]
    
    success_count = 0
    failure_count = 0
    
    print(f"\n===== 测试HTTP API ({base_url}) =====")
    
    for endpoint in endpoints:
        url = f"{base_url}{endpoint['url']}"
        method = endpoint['method']
        description = endpoint['description']
        
        print(f"\n-> 测试: {description} ({method.upper()} {url})")
        
        try:
            if method.lower() == 'get':
                response = requests.get(url, timeout=5)
            elif method.lower() == 'post':
                response = requests.post(url, timeout=5)
            else:
                print(f"  不支持的方法: {method}")
                failure_count += 1
                continue
            
            print(f"  状态码: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    response_json = response.json()
                    print(f"  响应: {json.dumps(response_json, ensure_ascii=False, indent=2)}")
                    success_count += 1
                except json.JSONDecodeError:
                    print(f"  响应不是有效的JSON: {response.text}")
                    failure_count += 1
            else:
                print(f"  错误响应: {response.text}")
                failure_count += 1
                
        except requests.exceptions.RequestException as e:
            print(f"  请求错误: {e}")
            failure_count += 1
    
    print(f"\n总结: 成功 {success_count}, 失败 {failure_count}")
    return success_count, failure_count

def test_websocket(base_url):
    """测试WebSocket连接和事件"""
    print(f"\n===== 测试WebSocket ({base_url}) =====")
    
    # 移除结尾的 http:// 或 https:// 并添加 'http://'
    if base_url.startswith('http://'):
        socket_url = base_url
    elif base_url.startswith('https://'):
        socket_url = 'http://' + base_url[8:]
    else:
        socket_url = 'http://' + base_url
    
    print(f"连接到WebSocket: {socket_url}")
    
    # 创建SocketIO客户端
    sio = socketio.Client()
    
    # 定义事件处理函数
    @sio.event
    def connect():
        print("  WebSocket已连接!")
    
    @sio.event
    def connect_error(data):
        print(f"  WebSocket连接错误: {data}")
    
    @sio.event
    def disconnect():
        print("  WebSocket已断开连接")
    
    @sio.on('welcome')
    def on_welcome(data):
        print(f"  收到欢迎消息: {data}")
    
    # 心率相关事件
    @sio.on('heart_rate_update')
    def on_heart_rate(data):
        print(f"  收到心率更新: {data}")
    
    # 床体相关事件
    @sio.on('bed_status_update')
    def on_bed_status(data):
        print(f"  收到床体状态更新: {data}")
    
    try:
        # 连接到WebSocket
        sio.connect(socket_url)
        
        # 等待初始连接消息
        print("  等待连接消息...")
        time.sleep(2)
        
        # 发送请求心率数据的事件
        print("  请求心率数据...")
        sio.emit('request_heart_rate')
        time.sleep(2)
        
        # 发送请求床体状态的事件
        print("  请求床体状态...")
        sio.emit('request_bed_status')
        time.sleep(2)
        
        # 断开连接
        sio.disconnect()
        return True
        
    except Exception as e:
        print(f"  WebSocket测试错误: {e}")
        return False

def main():
    args = parse_args()
    base_url = f"http://{args.host}:{args.port}"
    
    # 测试HTTP API
    success_count, failure_count = test_http_api(base_url)
    
    # 测试WebSocket (如果请求)
    websocket_success = False
    if args.test_websocket:
        websocket_success = test_websocket(base_url)
    
    # 判断测试是否成功
    if failure_count == 0 and (not args.test_websocket or websocket_success):
        print("\n所有测试通过!")
        return 0
    else:
        print("\n测试失败!")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 