const https = require('https');

const baseUrl = 'https://my-strapi-app-uaeb.onrender.com';

// Test public API endpoints (without authentication)
const publicEndpoints = [
  '/api/core-needs',
  '/api/personality-traits',
  '/api/dialogue-scenarios',
  '/api/ideal-responses',
  '/api/responses',
  '/api/trait-expressions',
  '/api/daily-challenges'
];

console.log('Testing Strapi API endpoints...\n');

publicEndpoints.forEach(endpoint => {
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
          console.log(`  ✅ Found ${json.data?.length || 0} items`);
          if (json.data && json.data.length > 0) {
            console.log(`  📝 First item: ${JSON.stringify(json.data[0].attributes || json.data[0]).substring(0, 100)}...`);
          }
        } catch (e) {
          console.log(`  ❌ Parse error: ${e.message}`);
        }
      });
    } else if (res.statusCode === 403) {
      console.log(`  🔒 Access forbidden - needs authentication`);
    } else if (res.statusCode === 404) {
      console.log(`  ❌ Not found - check permissions or content`);
    } else {
      console.log(`  ❓ Unexpected status: ${res.statusCode}`);
    }
  }).on('error', (err) => {
    console.log(`${endpoint}: ❌ Error - ${err.message}`);
  });
});

// Test admin panel
console.log('\nTesting admin panel...');
https.get(`${baseUrl}/admin`, (res) => {
  console.log(`Admin panel: ${res.statusCode}`);
  if (res.statusCode === 200) {
    console.log('  ✅ Admin panel accessible');
  } else {
    console.log(`  ❌ Admin panel issue: ${res.statusCode}`);
  }
}).on('error', (err) => {
  console.log(`Admin panel: ❌ Error - ${err.message}`);
}); 