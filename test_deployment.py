#!/usr/bin/env python3
"""
部署配置测试脚本
用于验证应用是否可以在生产环境中正常运行
"""

import os
import sys
import importlib.util

def test_imports():
    """测试所有必要的模块是否可以导入"""
    print("🔍 测试模块导入...")
    
    required_modules = [
        'flask',
        'requests', 
        'dotenv',
        'json',
        'random'
    ]
    
    for module in required_modules:
        try:
            importlib.import_module(module)
            print(f"✅ {module}")
        except ImportError as e:
            print(f"❌ {module}: {e}")
            return False
    
    return True

def test_env_vars():
    """测试环境变量配置"""
    print("\n🔍 测试环境变量...")
    
    # 加载 .env 文件
    from dotenv import load_dotenv
    load_dotenv()
    
    required_vars = [
        'STRAPI_URL',
        'STRAPI_API_TOKEN', 
        'ALIYUN_DASHSCOPE_API_KEY'
    ]
    
    missing_vars = []
    for var in required_vars:
        value = os.getenv(var)
        if value:
            print(f"✅ {var}: {'*' * len(value)}")  # 隐藏实际值
        else:
            print(f"❌ {var}: 未设置")
            missing_vars.append(var)
    
    if missing_vars:
        print(f"\n⚠️  警告：缺少环境变量: {', '.join(missing_vars)}")
        print("这些变量在生产环境中是必需的")
        return False
    
    return True

def test_files():
    """测试必要文件是否存在"""
    print("\n🔍 测试必要文件...")
    
    required_files = [
        'app.py',
        'child_main.py',
        'requirements.txt',
        'Procfile',
        'templates/index.html',
        'static/script.js'
    ]
    
    missing_files = []
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file}")
        else:
            print(f"❌ {file}")
            missing_files.append(file)
    
    if missing_files:
        print(f"\n❌ 错误：缺少文件: {', '.join(missing_files)}")
        return False
    
    return True

def test_flask_app():
    """测试 Flask 应用是否可以启动"""
    print("\n🔍 测试 Flask 应用...")
    
    try:
        # 临时设置环境变量用于测试
        os.environ.setdefault('FLASK_ENV', 'testing')
        
        # 导入应用
        from app import app
        
        # 测试应用配置
        with app.app_context():
            print("✅ Flask 应用创建成功")
            print(f"✅ 应用名称: {app.name}")
            print(f"✅ 调试模式: {app.debug}")
            
        return True
        
    except Exception as e:
        print(f"❌ Flask 应用测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🚀 亲子沟通模拟器 - 部署配置测试")
    print("=" * 50)
    
    tests = [
        ("模块导入", test_imports),
        ("环境变量", test_env_vars),
        ("必要文件", test_files),
        ("Flask 应用", test_flask_app)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 测试: {test_name}")
        print("-" * 30)
        
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} 测试通过")
            else:
                print(f"❌ {test_name} 测试失败")
        except Exception as e:
            print(f"❌ {test_name} 测试出错: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过！应用已准备好部署")
        print("\n📋 下一步：")
        print("1. 运行 ./deploy.sh 推送到 GitHub")
        print("2. 在 Render/Railway 上部署")
        print("3. 设置生产环境变量")
        return 0
    else:
        print("⚠️  部分测试失败，请修复问题后重试")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 