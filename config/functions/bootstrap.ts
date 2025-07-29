export default async ({ strapi }) => {
  // Disable upload plugin at runtime
  process.env.STRAPI_DISABLE_UPLOAD = 'true';
  process.env.STRAPI_UPLOAD_PROVIDER = 'local';
  process.env.STRAPI_UPLOAD_PROVIDER_OPTIONS = '{}';
  
  // Configure API permissions
  console.log('Configuring Strapi API permissions...');
  
  // Set public API access
  process.env.STRAPI_PUBLIC_API_ENABLED = 'true';
  process.env.STRAPI_PUBLIC_API_PERMISSIONS = 'find,findOne';
  
  // Force public access
  process.env.STRAPI_PUBLIC_ACCESS = 'true';
  process.env.STRAPI_DISABLE_PERMISSIONS = 'true';
  
  // Set up permissions for all content types
  try {
    const role = await strapi.query('plugin::users-permissions.role').findOne({
      where: { type: 'public' }
    });
    
    if (role) {
      // Grant all permissions to public role
      const permissions = {
        'api::core-need.core-need': { find: true, findOne: true, create: true, update: true, delete: true },
        'api::personality-trait.personality-trait': { find: true, findOne: true, create: true, update: true, delete: true },
        'api::daily-challenge.daily-challenge': { find: true, findOne: true, create: true, update: true, delete: true },
        'api::trait-expression.trait-expression': { find: true, findOne: true, create: true, update: true, delete: true },
        'api::dialogue-scenario.dialogue-scenario': { find: true, findOne: true, create: true, update: true, delete: true },
        'api::ideal-response.ideal-response': { find: true, findOne: true, create: true, update: true, delete: true },
        'api::response.response': { find: true, findOne: true, create: true, update: true, delete: true }
      };
      
      await strapi.query('plugin::users-permissions.role').update({
        where: { id: role.id },
        data: { permissions }
      });
      
      console.log('Permissions updated successfully');
    }
  } catch (error) {
    console.log('Error setting permissions:', error.message);
  }
  
  console.log('Bootstrap configuration completed');
}; 