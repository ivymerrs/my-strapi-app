export default {
  test: async (ctx) => {
    ctx.body = {
      message: 'Public API is working!',
      timestamp: new Date().toISOString(),
    };
  },

  getCoreNeeds: async (ctx) => {
    try {
      const coreNeeds = await strapi.entityService.findMany('api::core-need.core-need', {
        populate: '*',
      });
      
      ctx.body = {
        data: coreNeeds,
        success: true,
      };
    } catch (error) {
      ctx.body = {
        error: error.message,
        success: false,
      };
    }
  },
}; 