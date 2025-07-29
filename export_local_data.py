#!/usr/bin/env python3
"""
从本地 Strapi 导出数据并显示
"""

import requests
import json

# 本地 Strapi 配置
LOCAL_STRAPI_URL = "http://localhost:1337"

def get_local_data():
    """从本地 Strapi 获取数据"""
    print("🔍 从本地 Strapi 获取数据...")
    
    # 获取人格特质
    try:
        response = requests.get(f"{LOCAL_STRAPI_URL}/api/personality-traits")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 本地人格特质数据: {len(data.get('data', []))} 条")
            for item in data.get('data', []):
                print(f"   - {item.get('attributes', {}).get('name', 'Unknown')}")
        else:
            print(f"❌ 获取人格特质失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 连接本地 Strapi 失败: {e}")
        print("请确保本地 Strapi 正在运行 (npm run develop)")
        return
    
    # 获取日常挑战
    try:
        response = requests.get(f"{LOCAL_STRAPI_URL}/api/daily-challenges")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 本地日常挑战数据: {len(data.get('data', []))} 条")
            for item in data.get('data', []):
                print(f"   - {item.get('attributes', {}).get('name', 'Unknown')}")
        else:
            print(f"❌ 获取日常挑战失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 获取日常挑战出错: {e}")
    
    # 获取特质表达
    try:
        response = requests.get(f"{LOCAL_STRAPI_URL}/api/trait-expressions")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 本地特质表达数据: {len(data.get('data', []))} 条")
            for item in data.get('data', []):
                print(f"   - {item.get('attributes', {}).get('name', 'Unknown')}")
        else:
            print(f"❌ 获取特质表达失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 获取特质表达出错: {e}")

if __name__ == "__main__":
    get_local_data() 