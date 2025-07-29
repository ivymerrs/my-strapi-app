#!/usr/bin/env python3
"""
直接向 Render 上的 Strapi 添加测试数据
"""

import requests
import json
import time

# Strapi 配置
RENDER_STRAPI_URL = "https://my-strapi-app-uaeb.onrender.com"

def get_auth_token():
    """获取认证令牌"""
    login_data = {
        "identifier": "admin@example.com",
        "password": "Admin123!"
    }
    
    try:
        response = requests.post(f"{RENDER_STRAPI_URL}/api/auth/local", json=login_data)
        if response.status_code == 200:
            result = response.json()
            return result.get('jwt')
        else:
            print(f"❌ 登录失败: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ 登录出错: {e}")
        return None

def add_test_data(auth_token):
    """添加测试数据"""
    headers = {
        'Authorization': f'Bearer {auth_token}',
        'Content-Type': 'application/json'
    }
    
    # 测试数据
    test_data = {
        'personality-traits': [
            {
                "name": "外向型",
                "description": "喜欢社交，充满活力",
                "characteristics": "热情、健谈、乐观"
            },
            {
                "name": "内向型", 
                "description": "安静、深思熟虑",
                "characteristics": "谨慎、专注、独立"
            }
        ],
        'daily-challenges': [
            {
                "name": "情绪管理",
                "description": "学习控制情绪反应",
                "difficulty": "中等"
            },
            {
                "name": "沟通技巧",
                "description": "改善与孩子的沟通方式",
                "difficulty": "简单"
            }
        ],
        'trait-expressions': [
            {
                "name": "耐心倾听",
                "description": "在孩子说话时保持专注",
                "personality_trait": "内向型"
            },
            {
                "name": "积极鼓励",
                "description": "用正面语言鼓励孩子",
                "personality_trait": "外向型"
            },
            {
                "name": "情绪稳定",
                "description": "在孩子面前保持冷静",
                "personality_trait": "内向型"
            },
            {
                "name": "热情参与",
                "description": "积极参与孩子的活动",
                "personality_trait": "外向型"
            }
        ],
        'core-needs': [
            {
                "name": "安全感",
                "description": "孩子需要感到安全和被保护",
                "importance": "高"
            },
            {
                "name": "归属感",
                "description": "孩子需要感到被爱和接纳",
                "importance": "高"
            },
            {
                "name": "成就感",
                "description": "孩子需要感到有能力",
                "importance": "中"
            },
            {
                "name": "自主感",
                "description": "孩子需要感到有选择权",
                "importance": "中"
            }
        ],
        'dialogue-scenarios': [
            {
                "name": "孩子发脾气",
                "description": "孩子因为小事而情绪失控",
                "context": "家庭环境"
            },
            {
                "name": "孩子不想上学",
                "description": "孩子拒绝去学校",
                "context": "早晨时间"
            }
        ],
        'ideal-responses': [
            {
                "name": "冷静回应",
                "description": "保持冷静，理解孩子感受",
                "scenario": "孩子发脾气"
            },
            {
                "name": "积极引导",
                "description": "用积极方式引导孩子",
                "scenario": "孩子不想上学"
            },
            {
                "name": "情绪确认",
                "description": "确认并接纳孩子的情绪",
                "scenario": "孩子发脾气"
            },
            {
                "name": "设定边界",
                "description": "设定清晰的边界和期望",
                "scenario": "孩子不想上学"
            },
            {
                "name": "鼓励表达",
                "description": "鼓励孩子表达真实想法",
                "scenario": "孩子发脾气"
            }
        ],
        'responses': [
            {
                "name": "理解性回应",
                "description": "我理解你的感受",
                "tone": "温和"
            },
            {
                "name": "引导性回应",
                "description": "让我们一起想办法",
                "tone": "积极"
            },
            {
                "name": "支持性回应",
                "description": "我会一直支持你",
                "tone": "温暖"
            }
        ]
    }
    
    total_success = 0
    
    for data_type, items in test_data.items():
        print(f"\n📝 添加 {data_type} 测试数据...")
        
        success_count = 0
        for item in items:
            try:
                payload = {"data": item}
                response = requests.post(f"{RENDER_STRAPI_URL}/api/{data_type}", json=payload, headers=headers)
                
                if response.status_code == 200:
                    print(f"✅ 添加成功: {item.get('name', 'Unknown')}")
                    success_count += 1
                else:
                    print(f"❌ 添加失败: {item.get('name', 'Unknown')}, 状态码: {response.status_code}")
                    print(f"   错误: {response.text}")
            except Exception as e:
                print(f"❌ 添加出错: {item.get('name', 'Unknown')}, 错误: {e}")
        
        total_success += success_count
        print(f"✅ {data_type} 完成: {success_count}/{len(items)} 成功")
        time.sleep(1)  # 避免请求过快
    
    return total_success

def verify_data():
    """验证数据是否添加成功"""
    print(f"\n🔍 验证数据...")
    
    data_types = ['personality-traits', 'daily-challenges', 'trait-expressions', 'core-needs', 'dialogue-scenarios', 'ideal-responses', 'responses']
    
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

def main():
    print("🚀 开始添加测试数据...")
    print(f"📡 Render Strapi: {RENDER_STRAPI_URL}")
    
    # 获取认证令牌
    print("\n🔑 获取认证令牌...")
    auth_token = get_auth_token()
    if not auth_token:
        print("❌ 无法获取认证令牌，退出")
        return
    
    print("✅ 认证令牌获取成功")
    
    # 添加测试数据
    success_count = add_test_data(auth_token)
    
    print(f"\n🎉 测试数据添加完成！")
    print(f"📊 总计成功添加: {success_count} 条数据")
    
    # 验证数据
    verify_data()
    
    print(f"\n🔗 现在可以测试 Flask 应用:")
    print(f"   Flask 应用: https://parent-child-simulator.onrender.com")
    print(f"   Strapi API: {RENDER_STRAPI_URL}/api/public/personality-traits")

if __name__ == "__main__":
    main() 