export default () => {
  // Disable upload plugin at runtime
  process.env.STRAPI_DISABLE_UPLOAD = 'true';
}; 