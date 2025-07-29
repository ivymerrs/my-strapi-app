#!/bin/bash

echo "🔄 切换到 Node.js 20.19.4 版本..."

# 检查是否安装了 nvm
if ! command -v nvm &> /dev/null; then
    echo "❌ nvm 未安装，请先安装 nvm"
    echo "安装命令: curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash"
    exit 1
fi

# 加载 nvm
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"

# 安装 Node.js 20.19.4（如果不存在）
if ! nvm list | grep -q "v20.19.4"; then
    echo "📦 安装 Node.js 20.19.4..."
    nvm install 20.19.4
fi

# 切换到 Node.js 20.19.4
echo "🔄 切换到 Node.js 20.19.4..."
nvm use 20.19.4

# 设置默认版本
echo "🔧 设置 Node.js 20.19.4 为默认版本..."
nvm alias default 20.19.4

# 验证版本
echo "✅ 当前 Node.js 版本:"
node --version
npm --version

echo "🎉 Node.js 版本切换完成！"
echo "现在可以重新安装依赖并测试构建了。" 