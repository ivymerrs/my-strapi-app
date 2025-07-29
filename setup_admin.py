#!/usr/bin/env python3
"""
设置 Strapi 管理员账户
"""

import requests
import json

# Strapi 配置
STRAPI_URL = "https://my-strapi-app-uaeb.onrender.com"

def setup_admin():
    """设置管理员账户"""
    print("🚀 设置 Strapi 管理员账户...")
    
    # 检查是否已经有管理员
    try:
        response = requests.get(f"{STRAPI_URL}/api/users")
        if response.status_code == 200:
            data = response.json()
            users = data.get('data', [])
            if users:
                print(f"✅ 已存在 {len(users)} 个用户")
                for user in users:
                    attrs = user.get('attributes', {})
                    print(f"   - {attrs.get('username', 'Unknown')} ({attrs.get('email', 'No email')})")
                return True
        else:
            print(f"❌ 检查用户失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 检查用户出错: {e}")
    
    # 创建管理员账户
    admin_data = {
        "email": "admin@example.com",
        "username": "admin",
        "password": "Admin123!"
    }
    
    try:
        response = requests.post(f"{STRAPI_URL}/api/auth/local/register", json=admin_data)
        if response.status_code == 200:
            print("✅ 管理员账户创建成功！")
            result = response.json()
            print(f"   用户名: {result.get('user', {}).get('username')}")
            print(f"   邮箱: {result.get('user', {}).get('email')}")
            return True
        else:
            print(f"❌ 创建管理员账户失败: {response.status_code}")
            print(f"   错误: {response.text}")
            return False
    except Exception as e:
        print(f"❌ 创建管理员账户出错: {e}")
        return False

def get_api_token():
    """获取 API 令牌"""
    print("\n🔑 获取 API 令牌...")
    
    # 登录获取 JWT
    login_data = {
        "identifier": "admin@example.com",
        "password": "Admin123!"
    }
    
    try:
        response = requests.post(f"{STRAPI_URL}/api/auth/local", json=login_data)
        if response.status_code == 200:
            result = response.json()
            jwt_token = result.get('jwt')
            if jwt_token:
                print("✅ 登录成功，获取到 JWT 令牌")
                return jwt_token
            else:
                print("❌ 登录成功但未获取到 JWT 令牌")
                return None
        else:
            print(f"❌ 登录失败: {response.status_code}")
            print(f"   错误: {response.text}")
            return None
    except Exception as e:
        print(f"❌ 登录出错: {e}")
        return None

if __name__ == "__main__":
    # 设置管理员账户
    if setup_admin():
        # 获取 API 令牌
        token = get_api_token()
        if token:
            print(f"\n🎉 设置完成！")
            print(f"📝 JWT 令牌: {token[:50]}...")
            print(f"🔗 管理面板: {STRAPI_URL}/admin")
        else:
            print(f"\n❌ 获取 API 令牌失败")
    else:
        print(f"\n❌ 设置管理员账户失败") 