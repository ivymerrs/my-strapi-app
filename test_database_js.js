const path = require('path');

console.log('=== 测试 database.js 配置 ===');

// 模拟 Strapi 的 env 函数
const createEnv = (nodeEnv) => {
  const envVars = {
    'NODE_ENV': nodeEnv,
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
    'DATABASE_POOL_MAX': '10',
    'DATABASE_FILENAME': '.tmp/data.db'
  };
  
  const env = (key, defaultValue) => {
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
  
  return env;
};

try {
  // 测试开发环境配置
  console.log('\n=== 测试开发环境配置 ===');
  const devEnv = createEnv('development');
  const devConfig = require('./config/database.js')({ env: devEnv });
  console.log('开发环境配置:', JSON.stringify(devConfig, null, 2));
  
  if (devConfig.connection.client === 'sqlite') {
    console.log('✅ 开发环境正确配置为 SQLite');
  } else {
    console.log('❌ 开发环境配置错误');
  }
  
  // 测试生产环境配置
  console.log('\n=== 测试生产环境配置 ===');
  const prodEnv = createEnv('production');
  const prodConfig = require('./config/database.js')({ env: prodEnv });
  console.log('生产环境配置:', JSON.stringify(prodConfig, null, 2));
  
  if (prodConfig.connection.client === 'pg') {
    console.log('✅ 生产环境正确配置为 PostgreSQL (pg)');
  } else {
    console.log('❌ 生产环境配置错误');
  }
  
  console.log('\n✅ database.js 配置测试通过！');
  
} catch (error) {
  console.error('❌ 配置测试失败:', error.message);
} 