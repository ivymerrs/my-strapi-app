#!/usr/bin/env python3
"""
测试通过公开 API 创建数据
"""

import requests
import json

# Strapi 配置
RENDER_STRAPI_URL = "https://my-strapi-app-uaeb.onrender.com"

def test_public_create():
    """测试通过公开 API 创建数据"""
    print("🔍 测试通过公开 API 创建数据...")
    
    # 测试数据
    test_data = {
        "data": {
            "name": "测试人格特质",
            "description": "这是一个测试数据"
        }
    }
    
    try:
        # 尝试通过公开 API 创建数据
        response = requests.post(f"{RENDER_STRAPI_URL}/api/personality-traits", json=test_data)
        print(f"✅ 公开 API 创建测试: {response.status_code}")
        if response.status_code == 200:
            print("🎉 成功！可以通过公开 API 创建数据")
            return True
        else:
            print(f"   错误: {response.text}")
            return False
    except Exception as e:
        print(f"❌ 公开 API 创建测试出错: {e}")
        return False

def test_public_api_endpoints():
    """测试所有公开 API 端点"""
    print("\n🔍 测试所有公开 API 端点...")
    
    endpoints = [
        '/api/public/test',
        '/api/public/personality-traits',
        '/api/public/daily-challenges',
        '/api/public/trait-expressions',
        '/api/public/dialogue-scenarios',
        '/api/public/ideal-responses',
        '/api/public/responses',
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

if __name__ == "__main__":
    success = test_public_create()
    test_public_api_endpoints()
    
    if success:
        print("\n🎉 现在可以开始添加测试数据了！")
    else:
        print("\n❌ 仍然无法创建数据，需要进一步调试") 