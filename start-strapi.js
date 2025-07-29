#!/usr/bin/env node

// Custom Strapi start script with permissions configuration
process.env.STRAPI_DISABLE_UPLOAD = 'true';
process.env.STRAPI_PUBLIC_ACCESS = 'true';
process.env.STRAPI_DISABLE_PERMISSIONS = 'true';

const strapi = require('@strapi/strapi');

// Start Strapi
strapi().start(); 