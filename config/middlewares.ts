export default [
  'strapi::logger',
  'strapi::errors',
  'strapi::security',
  'strapi::cors',
  'strapi::poweredBy',
  'strapi::query',
  'strapi::body',
  'strapi::session',
  'strapi::favicon',
  'strapi::public',
  // Add custom middleware for API permissions
  {
    name: 'strapi::api-permissions',
    config: {
      enabled: true,
      publicAccess: true,
    },
  },
];
