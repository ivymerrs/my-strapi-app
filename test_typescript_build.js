const path = require('path');
const fs = require('fs');

console.log('=== TypeScript 构建测试 ===');

// 检查构建目录
const distPath = path.join(__dirname, 'dist');
const configPath = path.join(distPath, 'config');
const databasePath = path.join(configPath, 'database.js');

console.log('检查构建目录...');
if (fs.existsSync(distPath)) {
  console.log('✅ dist 目录存在');
  
  if (fs.existsSync(configPath)) {
    console.log('✅ config 目录存在');
    
    if (fs.existsSync(databasePath)) {
      console.log('✅ database.js 文件存在');
      
      // 读取编译后的数据库配置
      const databaseConfig = require('./dist/config/database.js').default;
      
      // 模拟环境变量
      const env = (key, defaultValue) => {
        const envVars = {
          'NODE_ENV': 'production',
          'DATABASE_URL': 'postgresql://test:test@localhost:5432/testdb',
          'DATABASE_HOST': 'localhost',
          'DATABASE_PORT': '5432',
          'DATABASE_NAME': 'strapi',
          'DATABASE_USERNAME': 'strapi',
          'DATABASE_PASSWORD': 'strapi',
          'DATABASE_SSL': 'true',
          'DATABASE_SSL_REJECT_UNAUTHORIZED': 'false',
          'DATABASE_SCHEMA': 'public',
          'DATABASE_POOL_MIN': '0',
          'DATABASE_POOL_MAX': '10'
        };
        return envVars[key] || defaultValue;
      };
      
      // 添加 env.int 和 env.bool 方法
      env.int = (key, defaultValue) => {
        const value = env(key, defaultValue);
        return parseInt(value, 10);
      };
      
      env.bool = (key, defaultValue) => {
        const value = env(key, defaultValue);
        return value === 'true' || value === true;
      };
      
      // 测试生产环境配置
      console.log('\n测试生产环境配置...');
      const prodConfig = databaseConfig({ env });
      console.log('生产环境配置:', JSON.stringify(prodConfig, null, 2));
      
      if (prodConfig.connection.client === 'postgres') {
        console.log('✅ 生产环境正确配置为 PostgreSQL');
      } else {
        console.log('❌ 生产环境配置错误');
      }
      
    } else {
      console.log('❌ database.js 文件不存在');
    }
  } else {
    console.log('❌ config 目录不存在');
  }
} else {
  console.log('❌ dist 目录不存在');
}

console.log('\n=== 测试完成 ==='); 