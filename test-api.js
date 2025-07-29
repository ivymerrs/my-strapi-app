const https = require('https');

const baseUrl = 'https://my-strapi-app-uaeb.onrender.com';

// Test basic API endpoints
const endpoints = [
  '/api/core-needs',
  '/api/personality-traits',
  '/api/dialogue-scenarios',
  '/api/ideal-responses',
  '/api/responses',
  '/api/trait-expressions',
  '/api/daily-challenges'
];

endpoints.forEach(endpoint => {
  const url = `${baseUrl}${endpoint}`;
  
  https.get(url, (res) => {
    console.log(`${endpoint}: ${res.statusCode}`);
    if (res.statusCode === 200) {
      let data = '';
      res.on('data', (chunk) => {
        data += chunk;
      });
      res.on('end', () => {
        try {
          const json = JSON.parse(data);
          console.log(`  - Found ${json.data?.length || 0} items`);
        } catch (e) {
          console.log(`  - Response: ${data.substring(0, 100)}...`);
        }
      });
    }
  }).on('error', (err) => {
    console.log(`${endpoint}: Error - ${err.message}`);
  });
}); 