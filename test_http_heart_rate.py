#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
HTTP心率API测试脚本 - 专门测试心率相关的HTTP API
"""

import requests
import json
import sys
import argparse
import time

def parse_args():
    parser = argparse.ArgumentParser(description='HTTP心率API测试')
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
    heart_rates = []
    
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
                        heart_rates.append(heart_rate)
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
    if heart_rates:
        print(f"获取到的心率值: {heart_rates}")
        print(f"平均心率: {sum(heart_rates)/len(heart_rates):.1f}")
    
    return success_count, failure_count

def main():
    args = parse_args()
    base_url = f"http://{args.host}:{args.port}"
    
    # 打印基本信息
    print(f"=== HTTP心率API测试 ===")
    print(f"API URL: {base_url}/api/heart-rate")
    print(f"测试次数: {args.iterations}")
    print(f"测试间隔: {args.interval}秒")
    print("=" * 30)
    
    # 测试HTTP API
    success_count, failure_count = test_http_heart_rate_api(
        base_url, 
        iterations=args.iterations, 
        interval=args.interval,
        debug=args.debug
    )
    
    # 判断测试是否成功
    if failure_count == 0 and success_count > 0:
        print("\n心率API测试通过!")
        return 0
    else:
        print("\n心率API测试存在问题!")
        print(f"  - 成功: {success_count}, 失败: {failure_count}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 