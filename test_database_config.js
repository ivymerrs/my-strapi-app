const { env } = require('@strapi/utils');

// 模拟环境变量
process.env.NODE_ENV = 'development';

// 测试开发环境配置
console.log('=== 测试开发环境配置 ===');
process.env.NODE_ENV = 'development';
const devConfig = require('./config/database.ts').default({ env });
console.log('开发环境配置:', JSON.stringify(devConfig, null, 2));

// 测试生产环境配置
console.log('\n=== 测试生产环境配置 ===');
process.env.NODE_ENV = 'production';
process.env.DATABASE_URL = 'postgresql://test:test@localhost:5432/testdb';
const prodConfig = require('./config/database.ts').default({ env });
console.log('生产环境配置:', JSON.stringify(prodConfig, null, 2));

console.log('\n✅ 数据库配置测试完成！'); 