#!/usr/bin/env python3
"""
向 Strapi 添加测试数据的脚本
"""

import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

# Strapi 配置
STRAPI_URL = "https://my-strapi-app-uaeb.onrender.com"

def add_personality_traits():
    """添加人格特质数据"""
    url = f"{STRAPI_URL}/api/personality-traits"
    
    personalities = [
        {
            "data": {
                "name": "内向敏感型",
                "description": "这类孩子比较内向，对周围环境敏感，容易受到情绪影响",
                "keycharacteristic": ["内向", "敏感", "情绪化"],
                "core_need_description": "需要安全感和理解"
            }
        },
        {
            "data": {
                "name": "外向活泼型",
                "description": "这类孩子外向开朗，喜欢社交，充满活力",
                "keycharacteristic": ["外向", "活泼", "社交"],
                "core_need_description": "需要关注和认可"
            }
        },
        {
            "data": {
                "name": "专注执着型",
                "description": "这类孩子专注力强，做事认真，有毅力",
                "keycharacteristic": ["专注", "执着", "认真"],
                "core_need_description": "需要成就感和支持"
            }
        },
        {
            "data": {
                "name": "创意想象型",
                "description": "这类孩子富有想象力，喜欢创造，思维活跃",
                "keycharacteristic": ["创意", "想象", "活跃"],
                "core_need_description": "需要表达和鼓励"
            }
        }
    ]
    
    for personality in personalities:
        try:
            response = requests.post(url, json=personality)
            if response.status_code == 200:
                print(f"✅ 添加人格特质成功: {personality['data']['name']}")
            else:
                print(f"❌ 添加人格特质失败: {personality['data']['name']}, 状态码: {response.status_code}")
        except Exception as e:
            print(f"❌ 添加人格特质出错: {personality['data']['name']}, 错误: {e}")

def add_daily_challenges():
    """添加日常挑战数据"""
    url = f"{STRAPI_URL}/api/daily-challenges"
    
    challenges = [
        {
            "data": {
                "name": "学习困难",
                "description": "孩子在学习和作业方面遇到困难"
            }
        },
        {
            "data": {
                "name": "社交焦虑",
                "description": "孩子在社交场合感到焦虑和不安"
            }
        },
        {
            "data": {
                "name": "情绪管理",
                "description": "孩子在情绪控制方面需要帮助"
            }
        },
        {
            "data": {
                "name": "注意力不集中",
                "description": "孩子难以集中注意力完成任务"
            }
        }
    ]
    
    for challenge in challenges:
        try:
            response = requests.post(url, json=challenge)
            if response.status_code == 200:
                print(f"✅ 添加日常挑战成功: {challenge['data']['name']}")
            else:
                print(f"❌ 添加日常挑战失败: {challenge['data']['name']}, 状态码: {response.status_code}")
        except Exception as e:
            print(f"❌ 添加日常挑战出错: {challenge['data']['name']}, 错误: {e}")

def add_trait_expressions():
    """添加特质表达数据"""
    url = f"{STRAPI_URL}/api/trait-expressions"
    
    expressions = [
        {
            "data": {
                "name": "内向敏感型表达",
                "default_expression": "轻声细语，容易害羞",
                "personality_trait": 1
            }
        },
        {
            "data": {
                "name": "外向活泼型表达",
                "default_expression": "声音洪亮，表情丰富",
                "personality_trait": 2
            }
        },
        {
            "data": {
                "name": "专注执着型表达",
                "default_expression": "认真专注，逻辑清晰",
                "personality_trait": 3
            }
        },
        {
            "data": {
                "name": "创意想象型表达",
                "default_expression": "思维跳跃，富有想象力",
                "personality_trait": 4
            }
        }
    ]
    
    for expression in expressions:
        try:
            response = requests.post(url, json=expression)
            if response.status_code == 200:
                print(f"✅ 添加特质表达成功: {expression['data']['name']}")
            else:
                print(f"❌ 添加特质表达失败: {expression['data']['name']}, 状态码: {response.status_code}")
        except Exception as e:
            print(f"❌ 添加特质表达出错: {expression['data']['name']}, 错误: {e}")

def main():
    print("🚀 开始向 Strapi 添加测试数据...")
    print(f"📡 Strapi URL: {STRAPI_URL}")
    
    # 添加人格特质
    print("\n📝 添加人格特质数据...")
    add_personality_traits()
    
    # 添加日常挑战
    print("\n📝 添加日常挑战数据...")
    add_daily_challenges()
    
    # 添加特质表达
    print("\n📝 添加特质表达数据...")
    add_trait_expressions()
    
    print("\n✅ 数据添加完成！")
    print("🔍 现在可以测试 API 了：")
    print(f"   - 人格特质: {STRAPI_URL}/api/public/personality-traits")
    print(f"   - 日常挑战: {STRAPI_URL}/api/public/daily-challenges")

if __name__ == "__main__":
    main() 