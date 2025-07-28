#!/bin/bash

# 亲子沟通模拟器 - 快速部署脚本

echo "🚀 亲子沟通模拟器 - 快速部署脚本"
echo "=================================="

# 检查是否在 Git 仓库中
if [ ! -d ".git" ]; then
    echo "❌ 错误：当前目录不是 Git 仓库"
    echo "请先初始化 Git 仓库："
    echo "  git init"
    echo "  git add ."
    echo "  git commit -m 'Initial commit'"
    exit 1
fi

# 检查是否有远程仓库
if ! git remote get-url origin > /dev/null 2>&1; then
    echo "⚠️  警告：没有设置远程仓库"
    echo "请先添加远程仓库："
    echo "  git remote add origin <your-github-repo-url>"
    echo "然后重新运行此脚本"
    exit 1
fi

# 检查 .env 文件是否存在
if [ -f ".env" ]; then
    echo "⚠️  警告：检测到 .env 文件"
    echo "请确保 .env 文件已添加到 .gitignore 中，避免敏感信息泄露"
    read -p "是否继续？(y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# 检查必要的文件
echo "📋 检查必要文件..."
required_files=("app.py" "requirements.txt" "Procfile" "templates/index.html" "static/script.js")
for file in "${required_files[@]}"; do
    if [ ! -f "$file" ]; then
        echo "❌ 错误：缺少必要文件 $file"
        exit 1
    fi
done
echo "✅ 所有必要文件都存在"

# 提交更改
echo "📝 提交代码更改..."
git add .
git commit -m "Deploy: 准备部署到生产环境"

# 推送到远程仓库
echo "🚀 推送到远程仓库..."
git push origin main

echo ""
echo "✅ 代码已推送到 GitHub！"
echo ""
echo "📋 下一步操作："
echo "1. 访问 https://render.com 或 https://railway.app"
echo "2. 连接您的 GitHub 仓库"
echo "3. 设置环境变量："
echo "   - STRAPI_URL"
echo "   - STRAPI_API_TOKEN"
echo "   - ALIYUN_DASHSCOPE_API_KEY"
echo "4. 部署应用"
echo ""
echo "📖 详细部署指南请参考 DEPLOYMENT.md"
echo ""
echo "🎉 祝您部署顺利！" 