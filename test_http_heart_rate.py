#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
HTTP Heart Rate API Test Script - Specifically tests heart rate related HTTP API
"""

import requests
import json
import sys
import argparse
import time

def parse_args():
    parser = argparse.ArgumentParser(description='HTTP Heart Rate API Test')
    parser.add_argument('--host', type=str, default='localhost', 
                        help='API server hostname or IP address')
    parser.add_argument('--port', type=int, default=5000, 
                        help='API server port')
    parser.add_argument('--iterations', type=int, default=10,
                        help='Number of test iterations')
    parser.add_argument('--interval', type=float, default=1.0,
                        help='Test interval (seconds)')
    parser.add_argument('--debug', action='store_true',
                        help='Enable debug output')
    return parser.parse_args()

def test_http_heart_rate_api(base_url, iterations=10, interval=1.0, debug=False):
    """Test heart rate HTTP API endpoint"""
    print(f"\n===== Testing Heart Rate HTTP API ({base_url}/api/heart-rate) =====")
    
    success_count = 0
    failure_count = 0
    heart_rates = []
    
    for i in range(iterations):
        print(f"\nIteration {i+1}/{iterations}:")
        
        try:
            if debug:
                print(f"  Request: GET {base_url}/api/heart-rate")
                
            response = requests.get(f"{base_url}/api/heart-rate", timeout=5)
            
            if debug:
                print(f"  Status code: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    response_json = response.json()
                    heart_rate = response_json.get('heart_rate')
                    status = response_json.get('status')
                    
                    print(f"  Heart rate: {heart_rate}, Status: {status}")
                    
                    if status == 'ok' and heart_rate is not None:
                        success_count += 1
                        heart_rates.append(heart_rate)
                    else:
                        failure_count += 1
                        print(f"  Error response: {json.dumps(response_json, ensure_ascii=False)}")
                        
                except json.JSONDecodeError:
                    print(f"  Response is not valid JSON: {response.text}")
                    failure_count += 1
            else:
                print(f"  Error response: {response.text}")
                failure_count += 1
                
        except requests.exceptions.RequestException as e:
            print(f"  Request error: {e}")
            failure_count += 1
            
        # Wait before next iteration
        if i < iterations - 1:
            time.sleep(interval)
    
    print(f"\nSummary: Success {success_count}, Failure {failure_count}")
    if heart_rates:
        print(f"Retrieved heart rates: {heart_rates}")
        print(f"Average heart rate: {sum(heart_rates)/len(heart_rates):.1f}")
    
    return success_count, failure_count

def main():
    args = parse_args()
    base_url = f"http://{args.host}:{args.port}"
    
    # Print basic information
    print(f"=== HTTP Heart Rate API Test ===")
    print(f"API URL: {base_url}/api/heart-rate")
    print(f"Test count: {args.iterations}")
    print(f"Test interval: {args.interval} seconds")
    print("=" * 30)
    
    # Test HTTP API
    success_count, failure_count = test_http_heart_rate_api(
        base_url, 
        iterations=args.iterations, 
        interval=args.interval,
        debug=args.debug
    )
    
    # Determine if test was successful
    if failure_count == 0 and success_count > 0:
        print("\nHeart rate API test passed!")
        return 0
    else:
        print("\nHeart rate API test has issues!")
        print(f"  - Success: {success_count}, Failure: {failure_count}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 