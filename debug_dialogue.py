#!/usr/bin/env python3
"""
调试对话模拟功能
"""

import requests
import json

# Flask 应用 URL
FLASK_URL = "https://parent-child-simulator.onrender.com"

def test_endpoints():
    """测试所有端点"""
    print("🔍 测试所有端点...")
    
    # 测试健康检查
    print("\n1. 健康检查:")
    try:
        response = requests.get(f"{FLASK_URL}/health")
        print(f"   状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   数据计数: personalities={data.get('personalities_count')}, challenges={data.get('daily_challenges_count')}")
            print(f"   模拟器初始化: {data.get('simulator_initialized')}")
    except Exception as e:
        print(f"   错误: {e}")
    
    # 测试人格数据
    print("\n2. 人格数据:")
    try:
        response = requests.get(f"{FLASK_URL}/get_personalities")
        print(f"   状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   数据条数: {len(data)}")
            for item in data:
                print(f"     - ID: {item.get('id')}, 名称: {item.get('name')}")
    except Exception as e:
        print(f"   错误: {e}")
    
    # 测试挑战数据
    print("\n3. 挑战数据:")
    try:
        response = requests.get(f"{FLASK_URL}/get_daily_challenges")
        print(f"   状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   数据条数: {len(data)}")
            for item in data:
                print(f"     - ID: {item.get('id')}, 名称: {item.get('name')}")
    except Exception as e:
        print(f"   错误: {e}")

def test_dialogue_simulation():
    """测试对话模拟"""
    print("\n4. 对话模拟测试:")
    
    test_cases = [
        {
            "name": "测试1 - 内向敏感型 + 学习困难",
            "data": {
                "parent_utterance": "你好，今天在学校怎么样？",
                "personality_id": 1,
                "daily_challenge_id": 1
            }
        },
        {
            "name": "测试2 - 外向活泼型 + 社交焦虑",
            "data": {
                "parent_utterance": "今天和朋友玩得开心吗？",
                "personality_id": 2,
                "daily_challenge_id": 2
            }
        }
    ]
    
    for test_case in test_cases:
        print(f"\n   {test_case['name']}:")
        try:
            response = requests.post(
                f"{FLASK_URL}/simulate_dialogue",
                json=test_case['data'],
                headers={'Content-Type': 'application/json'}
            )
            print(f"   状态码: {response.status_code}")
            print(f"   响应: {response.text}")
        except Exception as e:
            print(f"   错误: {e}")

if __name__ == "__main__":
    test_endpoints()
    test_dialogue_simulation() 