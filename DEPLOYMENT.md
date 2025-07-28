# 亲子沟通模拟器 - 部署指南

## 部署选项

### 1. Render (推荐 - 免费)

1. **注册 Render 账户**
   - 访问 https://render.com
   - 使用 GitHub 账户注册

2. **连接 GitHub 仓库**
   - 将代码推送到 GitHub
   - 在 Render 中连接该仓库

3. **创建 Web Service**
   - 选择 "New Web Service"
   - 选择您的 GitHub 仓库
   - 配置如下：
     - **Name**: parent-child-simulator
     - **Environment**: Python 3
     - **Build Command**: `pip install -r requirements.txt`
     - **Start Command**: `gunicorn app:app --bind 0.0.0.0:$PORT`

4. **设置环境变量**
   在 Render 的环境变量设置中添加：
   ```
   STRAPI_URL=你的Strapi服务器地址
   STRAPI_API_TOKEN=你的Strapi API Token
   ALIYUN_DASHSCOPE_API_KEY=你的阿里云API Key
   ```

5. **部署**
   - 点击 "Create Web Service"
   - 等待部署完成

### 2. Railway (免费额度)

1. **注册 Railway 账户**
   - 访问 https://railway.app
   - 使用 GitHub 账户注册

2. **导入项目**
   - 选择 "Deploy from GitHub repo"
   - 选择您的仓库

3. **配置环境变量**
   在 Railway 的环境变量设置中添加：
   ```
   STRAPI_URL=你的Strapi服务器地址
   STRAPI_API_TOKEN=你的Strapi API Token
   ALIYUN_DASHSCOPE_API_KEY=你的阿里云API Key
   ```

4. **自动部署**
   - Railway 会自动检测并部署

### 3. Heroku (付费)

1. **安装 Heroku CLI**
2. **创建 Heroku 应用**
   ```bash
   heroku create your-app-name
   ```
3. **设置环境变量**
   ```bash
   heroku config:set STRAPI_URL=你的Strapi服务器地址
   heroku config:set STRAPI_API_TOKEN=你的Strapi API Token
   heroku config:set ALIYUN_DASHSCOPE_API_KEY=你的阿里云API Key
   ```
4. **部署**
   ```bash
   git push heroku main
   ```

## 环境变量说明

### 必需的环境变量：

1. **STRAPI_URL**
   - 描述：Strapi CMS 服务器的地址
   - 示例：`https://your-strapi-app.onrender.com`
   - 注意：如果 Strapi 也在云上，确保使用 HTTPS

2. **STRAPI_API_TOKEN**
   - 描述：Strapi API 访问令牌
   - 获取方式：在 Strapi 管理面板 → Settings → API Tokens 中创建

3. **ALIYUN_DASHSCOPE_API_KEY**
   - 描述：阿里云 DashScope API 密钥
   - 获取方式：阿里云控制台 → 产品与服务 → 通义千问

## 部署前检查清单

- [ ] 代码已推送到 GitHub
- [ ] requirements.txt 文件存在且包含所有依赖
- [ ] Procfile 文件存在
- [ ] runtime.txt 文件存在（如果使用 Heroku）
- [ ] 环境变量已正确设置
- [ ] Strapi 服务器可访问
- [ ] 阿里云 API 密钥有效

## 故障排除

### 常见问题：

1. **应用无法启动**
   - 检查环境变量是否正确设置
   - 查看部署日志中的错误信息

2. **Strapi 连接失败**
   - 确保 STRAPI_URL 使用 HTTPS
   - 检查 STRAPI_API_TOKEN 是否有效
   - 确认 Strapi 服务器正在运行

3. **LLM 功能不工作**
   - 检查 ALIYUN_DASHSCOPE_API_KEY 是否正确
   - 确认阿里云账户有足够的余额

4. **CORS 错误**
   - 应用已配置 CORS，应该不会有此问题
   - 如果仍有问题，检查前端请求的 URL

## 安全注意事项

1. **环境变量安全**
   - 不要在代码中硬编码敏感信息
   - 使用环境变量存储 API 密钥

2. **HTTPS 使用**
   - 生产环境必须使用 HTTPS
   - 确保 Strapi 服务器也使用 HTTPS

3. **API 限制**
   - 考虑添加 API 调用频率限制
   - 监控 API 使用量

## 性能优化

1. **缓存策略**
   - 应用已实现数据缓存
   - 考虑添加 Redis 缓存（可选）

2. **数据库优化**
   - 如果 Strapi 使用数据库，确保索引优化

3. **CDN 使用**
   - 考虑使用 CDN 加速静态资源

## 监控和维护

1. **日志监控**
   - 定期检查应用日志
   - 设置错误告警

2. **性能监控**
   - 监控响应时间
   - 监控 API 调用成功率

3. **备份策略**
   - 定期备份 Strapi 数据
   - 备份环境变量配置 