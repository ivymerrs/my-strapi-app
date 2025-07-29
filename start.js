#!/usr/bin/env node

// Custom start script to bypass upload plugin issues
process.env.STRAPI_DISABLE_UPLOAD = 'true';

const strapi = require('@strapi/strapi');

// Start Strapi
strapi().start(); 