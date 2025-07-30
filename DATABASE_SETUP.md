# 数据库配置说明

## 当前配置状态

✅ **数据库配置文件已更新** (`config/database.ts`)
✅ **PostgreSQL 客户端已安装** (`pg` 包)
✅ **环境检测逻辑已实现**

## 配置说明

### 开发环境 (NODE_ENV=development)
- 使用 **SQLite** 数据库
- 数据库文件位置：`.tmp/data.db`
- 适合本地开发和测试

### 生产环境 (NODE_ENV=production)
- 使用 **PostgreSQL** 数据库
- 支持 Render 的 Internal Database
- 连接字符串：`DATABASE_URL`

## 环境变量配置

### 开发环境
```bash
NODE_ENV=development
```

### 生产环境
```bash
NODE_ENV=production
DATABASE_URL=postgresql://username:password@host:port/database
DATABASE_HOST=your_host
DATABASE_PORT=5432
DATABASE_NAME=your_database_name
DATABASE_USERNAME=your_username
DATABASE_PASSWORD=your_password
DATABASE_SSL=true
DATABASE_SSL_REJECT_UNAUTHORIZED=false
```

## Render 部署配置

在 Render 控制台中，为 Strapi 服务添加以下环境变量：

1. **NODE_ENV**: `production`
2. **DATABASE_URL**: Render 提供的 Internal Database URL
3. **DATABASE_SSL**: `true`
4. **DATABASE_SSL_REJECT_UNAUTHORIZED**: `false`

## 测试配置

运行以下命令测试数据库配置：

```bash
# 测试开发环境
NODE_ENV=development npm run develop

# 测试生产环境（需要设置 DATABASE_URL）
NODE_ENV=production DATABASE_URL=your_connection_string npm run develop
```

## 下一步

1. 在 Render 控制台中配置 PostgreSQL 数据库
2. 设置正确的环境变量
3. 重新部署 Strapi 服务
4. 测试数据库连接

## 注意事项

- 确保 PostgreSQL 数据库已创建
- 检查数据库用户权限
- 验证网络连接和防火墙设置
- 测试 SSL 连接配置 