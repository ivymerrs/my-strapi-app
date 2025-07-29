# 亲子沟通模拟器

一个基于 AI 的亲子沟通模拟工具，帮助家长学习如何与不同人格特质的孩子进行有效沟通。

## 功能特点

- 🎯 **人格特质模拟**：支持多种孩子人格类型的模拟
- 🧠 **AI 驱动对话**：使用阿里云千问模型生成真实的对话回应
- 📊 **智能评估**：提供详细的沟通质量评估和改进建议
- 🎨 **现代化界面**：美观的用户界面，支持响应式设计
- 🔄 **实时反馈**：即时显示孩子回应和评估结果

## 技术栈

- **后端**：Flask (Python)
- **前端**：HTML5, CSS3, JavaScript
- **AI 模型**：阿里云千问 (Qwen)
- **数据管理**：Strapi CMS
- **部署**：支持 Render, Railway, Heroku 等平台

## 快速开始

### 本地开发

1. **克隆项目**
   ```bash
   git clone <your-repo-url>
   cd my-project
   ```

2. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

3. **配置环境变量**
   创建 `.env` 文件：
   ```bash
   STRAPI_URL=http://localhost:1337
   STRAPI_API_TOKEN=your_strapi_api_token
   ALIYUN_DASHSCOPE_API_KEY=your_aliyun_api_key
   ```

4. **启动应用**
   ```bash
   python app.py
   ```

5. **访问应用**
   打开浏览器访问 `http://localhost:5000`

### 生产部署

详细的部署指南请参考 [DEPLOYMENT.md](./DEPLOYMENT.md)

## 项目结构

```
my-project/
├── app.py                 # Flask 主应用
├── child_main.py          # 核心模拟逻辑
├── requirements.txt       # Python 依赖
├── Procfile              # 部署配置
├── runtime.txt           # Python 版本
├── templates/
│   └── index.html        # 主页面模板
├── static/
│   └── script.js         # 前端 JavaScript
├── config/               # Strapi 配置
└── README.md            # 项目说明
```

## 环境变量

| 变量名 | 描述 | 必需 |
|--------|------|------|
| `STRAPI_URL` | Strapi 服务器地址 | ✅ |
| `STRAPI_API_TOKEN` | Strapi API 令牌 | ✅ |
| `ALIYUN_DASHSCOPE_API_KEY` | 阿里云 API 密钥 | ✅ |

## 使用说明

1. **选择孩子人格**：从下拉菜单中选择孩子的人格类型
2. **选择挑战主题**：选择当前面临的挑战或情境
3. **输入家长话语**：在文本框中输入您想对孩子说的话
4. **开始模拟**：点击"开始模拟对话"按钮
5. **查看结果**：系统会显示孩子的回应和详细的评估分析

## 评估维度

- **沟通评估**：整体沟通质量评分
- **父级输入分析**：识别的人格特质和核心需求
- **积极方面**：沟通中的优点
- **改进建议**：可以改进的地方
- **孩子内心独白**：孩子的内心感受

## 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 支持

如果您遇到问题或有建议，请：

1. 查看 [DEPLOYMENT.md](./DEPLOYMENT.md) 中的故障排除部分
2. 检查环境变量配置
3. 查看应用日志
4. 提交 Issue 或联系维护者

## 更新日志

### v1.0.0
- 初始版本发布
- 支持基本的人格模拟功能
- 集成阿里云千问 AI 模型
- 现代化用户界面
- 详细的评估分析功能
# Force Render to use latest version
