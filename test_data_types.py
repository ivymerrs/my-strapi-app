#!/usr/bin/env python3
"""
测试数据类型问题
"""

import requests
import json

# Flask 应用 URL
FLASK_URL = "https://parent-child-simulator.onrender.com"

def test_data_types():
    """测试数据类型"""
    print("🔍 测试数据类型...")
    
    # 获取人格数据
    response = requests.get(f"{FLASK_URL}/get_personalities")
    if response.status_code == 200:
        personalities = response.json()
        print(f"人格数据类型:")
        for p in personalities:
            print(f"  ID: {p.get('id')} (类型: {type(p.get('id'))})")
            print(f"  名称: {p.get('name')} (类型: {type(p.get('name'))})")
    
    # 获取挑战数据
    response = requests.get(f"{FLASK_URL}/get_daily_challenges")
    if response.status_code == 200:
        challenges = response.json()
        print(f"\n挑战数据类型:")
        for c in challenges:
            print(f"  ID: {c.get('id')} (类型: {type(c.get('id'))})")
            print(f"  名称: {c.get('name')} (类型: {type(c.get('name'))})")

def test_dialogue_with_different_types():
    """测试不同数据类型的对话请求"""
    print("\n🔍 测试不同数据类型的对话请求...")
    
    test_cases = [
        {
            "name": "字符串ID",
            "data": {
                "parent_utterance": "你好，今天在学校怎么样？",
                "personality_id": "1",
                "daily_challenge_id": "1"
            }
        },
        {
            "name": "整数ID",
            "data": {
                "parent_utterance": "你好，今天在学校怎么样？",
                "personality_id": 1,
                "daily_challenge_id": 1
            }
        }
    ]
    
    for test_case in test_cases:
        print(f"\n{test_case['name']}:")
        try:
            response = requests.post(
                f"{FLASK_URL}/simulate_dialogue",
                json=test_case['data'],
                headers={'Content-Type': 'application/json'}
            )
            print(f"  状态码: {response.status_code}")
            print(f"  响应: {response.text}")
        except Exception as e:
            print(f"  错误: {e}")

if __name__ == "__main__":
    test_data_types()
    test_dialogue_with_different_types() 