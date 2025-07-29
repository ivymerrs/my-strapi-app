#!/usr/bin/env python3
"""
测试 Strapi 权限配置
"""

import requests
import json

# Strapi 配置
RENDER_STRAPI_URL = "https://my-strapi-app-uaeb.onrender.com"

def test_public_api():
    """测试公开 API"""
    print("🔍 测试公开 API...")
    
    endpoints = [
        '/api/public/test',
        '/api/public/personality-traits',
        '/api/public/daily-challenges',
        '/api/public/core-needs'
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"{RENDER_STRAPI_URL}{endpoint}")
            print(f"✅ {endpoint}: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                if 'data' in data:
                    print(f"   数据条数: {len(data.get('data', []))}")
        except Exception as e:
            print(f"❌ {endpoint}: 错误 - {e}")

def test_auth_api():
    """测试需要认证的 API"""
    print("\n🔑 测试认证 API...")
    
    # 获取认证令牌
    login_data = {
        "identifier": "admin@example.com",
        "password": "Admin123!"
    }
    
    try:
        response = requests.post(f"{RENDER_STRAPI_URL}/api/auth/local", json=login_data)
        if response.status_code == 200:
            result = response.json()
            auth_token = result.get('jwt')
            print("✅ 获取认证令牌成功")
            
            # 测试添加数据
            headers = {
                'Authorization': f'Bearer {auth_token}',
                'Content-Type': 'application/json'
            }
            
            test_data = {
                "data": {
                    "name": "测试人格特质",
                    "description": "这是一个测试数据"
                }
            }
            
            response = requests.post(f"{RENDER_STRAPI_URL}/api/personality-traits", json=test_data, headers=headers)
            print(f"✅ 添加数据测试: {response.status_code}")
            if response.status_code != 200:
                print(f"   错误: {response.text}")
        else:
            print(f"❌ 获取认证令牌失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 认证测试出错: {e}")

if __name__ == "__main__":
    test_public_api()
    test_auth_api() 