#!/usr/bin/env python3
"""
将本地 Strapi 数据迁移到 Render 上的 Strapi
"""

import requests
import json
import time

# 配置
LOCAL_STRAPI_URL = "http://localhost:1337"
RENDER_STRAPI_URL = "https://my-strapi-app-uaeb.onrender.com"

def get_local_data(endpoint):
    """从本地 Strapi 获取数据"""
    try:
        response = requests.get(f"{LOCAL_STRAPI_URL}/api/{endpoint}")
        if response.status_code == 200:
            return response.json().get('data', [])
        else:
            print(f"❌ 获取本地 {endpoint} 失败: {response.status_code}")
            return []
    except Exception as e:
        print(f"❌ 连接本地 Strapi 失败: {e}")
        return []

def add_data_to_render(endpoint, data_list):
    """将数据添加到 Render 上的 Strapi"""
    url = f"{RENDER_STRAPI_URL}/api/{endpoint}"
    
    success_count = 0
    for item in data_list:
        try:
            # 准备数据格式
            payload = {
                "data": item.get('attributes', {})
            }
            
            response = requests.post(url, json=payload)
            if response.status_code == 200:
                print(f"✅ 添加 {endpoint} 成功: {item.get('attributes', {}).get('name', 'Unknown')}")
                success_count += 1
            else:
                print(f"❌ 添加 {endpoint} 失败: {item.get('attributes', {}).get('name', 'Unknown')}, 状态码: {response.status_code}")
                print(f"   错误: {response.text}")
        except Exception as e:
            print(f"❌ 添加 {endpoint} 出错: {item.get('attributes', {}).get('name', 'Unknown')}, 错误: {e}")
    
    return success_count

def migrate_data():
    """迁移所有数据"""
    print("🚀 开始数据迁移...")
    print(f"📡 本地 Strapi: {LOCAL_STRAPI_URL}")
    print(f"📡 Render Strapi: {RENDER_STRAPI_URL}")
    
    # 定义要迁移的数据类型
    data_types = [
        'personality-traits',
        'daily-challenges', 
        'trait-expressions',
        'dialogue-scenarios',
        'ideal-responses',
        'responses',
        'core-needs'
    ]
    
    total_success = 0
    
    for data_type in data_types:
        print(f"\n📝 迁移 {data_type}...")
        
        # 获取本地数据
        local_data = get_local_data(data_type)
        if not local_data:
            print(f"⚠️  本地 {data_type} 数据为空，跳过")
            continue
        
        print(f"📊 本地 {data_type} 数据: {len(local_data)} 条")
        
        # 添加到 Render
        success_count = add_data_to_render(data_type, local_data)
        total_success += success_count
        
        print(f"✅ {data_type} 迁移完成: {success_count}/{len(local_data)} 成功")
        
        # 添加延迟避免请求过快
        time.sleep(1)
    
    print(f"\n🎉 数据迁移完成！")
    print(f"📊 总计成功迁移: {total_success} 条数据")
    
    # 验证迁移结果
    print(f"\n🔍 验证迁移结果...")
    for data_type in data_types:
        try:
            response = requests.get(f"{RENDER_STRAPI_URL}/api/public/{data_type}")
            if response.status_code == 200:
                data = response.json()
                count = len(data.get('data', []))
                print(f"✅ {data_type}: {count} 条数据")
            else:
                print(f"❌ {data_type}: 验证失败 ({response.status_code})")
        except Exception as e:
            print(f"❌ {data_type}: 验证出错 ({e})")

if __name__ == "__main__":
    migrate_data() 