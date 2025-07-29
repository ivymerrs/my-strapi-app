export default () => {
  // Disable upload plugin at runtime
  process.env.STRAPI_DISABLE_UPLOAD = 'true';
  process.env.STRAPI_UPLOAD_PROVIDER = 'local';
  process.env.STRAPI_UPLOAD_PROVIDER_OPTIONS = '{}';
  
  // Configure API permissions
  console.log('Configuring Strapi API permissions...');
  
  // Set public API access
  process.env.STRAPI_PUBLIC_API_ENABLED = 'true';
  process.env.STRAPI_PUBLIC_API_PERMISSIONS = 'find,findOne';
}; 