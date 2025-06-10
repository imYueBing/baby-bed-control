#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
心率API测试脚本 - 专门测试心率相关的HTTP API和WebSocket接口
"""

import requests
import json
import sys
import argparse
import socketio
import time

def parse_args():
    parser = argparse.ArgumentParser(description='心率API测试')
    parser.add_argument('--host', type=str, default='localhost', 
                        help='API服务器主机名或IP地址')
    parser.add_argument('--port', type=int, default=5000, 
                        help='API服务器端口')
    parser.add_argument('--iterations', type=int, default=10,
                        help='测试迭代次数')
    parser.add_argument('--interval', type=float, default=1.0,
                        help='测试间隔（秒）')
    parser.add_argument('--debug', action='store_true',
                        help='启用调试输出')
    return parser.parse_args()

def test_http_heart_rate_api(base_url, iterations=10, interval=1.0, debug=False):
    """测试心率HTTP API端点"""
    print(f"\n===== 测试心率HTTP API ({base_url}/api/heart-rate) =====")
    
    success_count = 0
    failure_count = 0
    
    for i in range(iterations):
        print(f"\n迭代 {i+1}/{iterations}:")
        
        try:
            if debug:
                print(f"  请求: GET {base_url}/api/heart-rate")
                
            response = requests.get(f"{base_url}/api/heart-rate", timeout=5)
            
            if debug:
                print(f"  状态码: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    response_json = response.json()
                    heart_rate = response_json.get('heart_rate')
                    status = response_json.get('status')
                    
                    print(f"  心率: {heart_rate}, 状态: {status}")
                    
                    if status == 'ok' and heart_rate is not None:
                        success_count += 1
                    else:
                        failure_count += 1
                        print(f"  错误响应: {json.dumps(response_json, ensure_ascii=False)}")
                        
                except json.JSONDecodeError:
                    print(f"  响应不是有效的JSON: {response.text}")
                    failure_count += 1
            else:
                print(f"  错误响应: {response.text}")
                failure_count += 1
                
        except requests.exceptions.RequestException as e:
            print(f"  请求错误: {e}")
            failure_count += 1
            
        # 在下一次迭代之前等待
        if i < iterations - 1:
            time.sleep(interval)
    
    print(f"\n总结: 成功 {success_count}, 失败 {failure_count}")
    return success_count, failure_count

def test_websocket_heart_rate(base_url, iterations=10, interval=1.0, debug=False):
    """测试WebSocket心率事件"""
    print(f"\n===== 测试WebSocket心率事件 ({base_url}) =====")
    
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
    
    # 记录结果
    results = {
        'connected': False,
        'heart_rate_updates': 0,
        'last_heart_rate': None,
        'errors': []
    }
    
    # 定义事件处理函数
    @sio.event
    def connect():
        print("  WebSocket已连接!")
        results['connected'] = True
    
    @sio.event
    def connect_error(data):
        error_msg = f"  WebSocket连接错误: {data}"
        print(error_msg)
        results['errors'].append(error_msg)
    
    @sio.event
    def disconnect():
        print("  WebSocket已断开连接")
    
    # 心率相关事件
    @sio.on('heart_rate_update')
    def on_heart_rate(data):
        results['heart_rate_updates'] += 1
        results['last_heart_rate'] = data.get('heart_rate')
        print(f"  收到心率更新: {data}")
    
    try:
        # 连接到WebSocket
        sio.connect(socket_url)
        
        # 等待初始连接消息
        print("  等待连接...")
        time.sleep(1)
        
        # 多次请求心率数据
        for i in range(iterations):
            print(f"\n  迭代 {i+1}/{iterations}: 请求心率数据...")
            sio.emit('request_heart_rate')
            
            # 等待服务器响应
            time.sleep(interval)
        
        # 延迟一下以确保接收到最后的响应
        time.sleep(1)
        
        # 断开连接
        sio.disconnect()
        
        print(f"\n总结:")
        print(f"  连接成功: {'是' if results['connected'] else '否'}")
        print(f"  接收到心率更新次数: {results['heart_rate_updates']}")
        print(f"  最后一次心率值: {results['last_heart_rate']}")
        
        if results['errors']:
            print(f"  错误:")
            for error in results['errors']:
                print(f"    - {error}")
        
        return results['connected'] and results['heart_rate_updates'] > 0
        
    except Exception as e:
        print(f"  WebSocket测试错误: {e}")
        return False

def diagnostic_info(args):
    """打印诊断信息"""
    print("\n===== 诊断信息 =====")
    print(f"主机: {args.host}")
    print(f"端口: {args.port}")
    print(f"完整URL: http://{args.host}:{args.port}")
    print(f"测试迭代次数: {args.iterations}")
    print(f"测试间隔: {args.interval}秒")
    
    # 检查网络连接
    print("\n检查网络连接...")
    try:
        response = requests.get(f"http://{args.host}:{args.port}", timeout=2)
        print(f"  基本连接: 成功 (状态码: {response.status_code})")
    except requests.exceptions.RequestException as e:
        print(f"  基本连接: 失败 ({e})")

def main():
    args = parse_args()
    base_url = f"http://{args.host}:{args.port}"
    
    # 打印诊断信息
    diagnostic_info(args)
    
    # 测试HTTP API
    http_success, http_failure = test_http_heart_rate_api(
        base_url, 
        iterations=args.iterations, 
        interval=args.interval,
        debug=args.debug
    )
    
    # 测试WebSocket
    websocket_success = test_websocket_heart_rate(
        base_url, 
        iterations=args.iterations, 
        interval=args.interval,
        debug=args.debug
    )
    
    # 判断测试是否成功
    if http_failure == 0 and websocket_success:
        print("\n所有心率API测试通过!")
        return 0
    else:
        print("\n心率API测试存在问题!")
        if http_failure > 0:
            print(f"  - HTTP API测试: {http_failure}个失败")
        if not websocket_success:
            print(f"  - WebSocket测试失败")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 