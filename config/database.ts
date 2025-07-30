import path from 'path';

export default ({ env }) => {
  // 检测环境
  const isDevelopment = env('NODE_ENV') === 'development';
  const isProduction = env('NODE_ENV') === 'production';

  // 开发环境配置（使用 SQLite）
  if (isDevelopment) {
    return {
      connection: {
        client: 'sqlite',
        connection: {
          filename: path.join(__dirname, '..', '..', env('DATABASE_FILENAME', '.tmp/data.db')),
        },
        useNullAsDefault: true,
      },
    };
  }

  // 生产环境配置（使用 PostgreSQL）
  if (isProduction) {
    return {
      connection: {
        client: 'postgres',
        connection: {
          // 使用 Render 提供的 Internal Database URL
          connectionString: env('DATABASE_URL'),
          // 备用连接参数（如果 DATABASE_URL 不可用）
          host: env('DATABASE_HOST', 'localhost'),
          port: env.int('DATABASE_PORT', 5432),
          database: env('DATABASE_NAME', 'strapi'),
          user: env('DATABASE_USERNAME', 'strapi'),
          password: env('DATABASE_PASSWORD', 'strapi'),
          ssl: env.bool('DATABASE_SSL', false) && {
            rejectUnauthorized: env.bool('DATABASE_SSL_REJECT_UNAUTHORIZED', false),
          },
          schema: env('DATABASE_SCHEMA', 'public'),
        },
        pool: {
          min: env.int('DATABASE_POOL_MIN', 0),
          max: env.int('DATABASE_POOL_MAX', 10),
          acquireTimeoutMillis: 600000,
          createTimeoutMillis: 30000,
          destroyTimeoutMillis: 5000,
          idleTimeoutMillis: 30000,
          reapIntervalMillis: 1000,
          createRetryIntervalMillis: 100,
        },
        debug: false,
      },
    };
  }

  // 默认配置（回退到 SQLite）
  return {
    connection: {
      client: 'sqlite',
      connection: {
        filename: path.join(__dirname, '..', '..', env('DATABASE_FILENAME', '.tmp/data.db')),
      },
      useNullAsDefault: true,
    },
  };
};
