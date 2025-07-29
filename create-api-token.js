const crypto = require('crypto');

// Generate a random API token
const generateApiToken = () => {
  return crypto.randomBytes(32).toString('hex');
};

// Generate salt values
const generateSalt = () => {
  return crypto.randomBytes(16).toString('base64');
};

console.log('=== Strapi Configuration Values ===');
console.log('');
console.log('API Token (for STRAPI_API_TOKEN):');
console.log(generateApiToken());
console.log('');
console.log('Admin JWT Secret (for ADMIN_JWT_SECRET):');
console.log(generateSalt());
console.log('');
console.log('API Token Salt (for API_TOKEN_SALT):');
console.log(generateSalt());
console.log('');
console.log('Transfer Token Salt (for TRANSFER_TOKEN_SALT):');
console.log(generateSalt());
console.log('');
console.log('=== Instructions ===');
console.log('1. Copy these values to your Render environment variables');
console.log('2. Update both Strapi and Flask applications');
console.log('3. Restart both services'); 