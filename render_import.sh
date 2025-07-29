#!/bin/bash

# 在 Render 上执行 Strapi 导入的脚本

echo "🚀 在 Render 上执行 Strapi 数据导入..."

# 检查导出文件是否存在
if [ ! -f "export_20250729160733.tar.gz" ]; then
    echo "❌ 导出文件不存在: export_20250729160733.tar.gz"
    exit 1
fi

echo "✅ 找到导出文件: export_20250729160733.tar.gz"

# 显示文件信息
ls -la export_20250729160733.tar.gz

echo ""
echo "📋 下一步操作："
echo "1. 登录 Render 控制台"
echo "2. 找到 my-strapi-app 服务"
echo "3. 进入 'Files' 标签"
echo "4. 下载 export_20250729160733.tar.gz 文件"
echo "5. 在 Strapi 管理面板中导入数据"
echo ""
echo "🔗 Strapi 管理面板: https://my-strapi-app-uaeb.onrender.com/admin"
echo "📧 管理员账户: admin@example.com"
echo "🔑 密码: Admin123!"
echo ""
echo "📝 导入步骤："
echo "1. 访问管理面板"
echo "2. 使用管理员账户登录"
echo "3. 进入 Settings → Global Settings → Import"
echo "4. 上传 export_20250729160733.tar.gz 文件"
echo "5. 点击导入按钮" 