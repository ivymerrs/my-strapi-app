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

  getPersonalityTraits: async (ctx) => {
    try {
      const traits = await strapi.entityService.findMany('api::personality-trait.personality-trait', {
        populate: '*',
      });
      
      ctx.body = {
        data: traits,
        success: true,
      };
    } catch (error) {
      ctx.body = {
        error: error.message,
        success: false,
      };
    }
  },

  getDialogueScenarios: async (ctx) => {
    try {
      const scenarios = await strapi.entityService.findMany('api::dialogue-scenario.dialogue-scenario', {
        populate: '*',
      });
      
      ctx.body = {
        data: scenarios,
        success: true,
      };
    } catch (error) {
      ctx.body = {
        error: error.message,
        success: false,
      };
    }
  },

  getIdealResponses: async (ctx) => {
    try {
      const responses = await strapi.entityService.findMany('api::ideal-response.ideal-response', {
        populate: '*',
      });
      
      ctx.body = {
        data: responses,
        success: true,
      };
    } catch (error) {
      ctx.body = {
        error: error.message,
        success: false,
      };
    }
  },

  getResponses: async (ctx) => {
    try {
      const responses = await strapi.entityService.findMany('api::response.response', {
        populate: '*',
      });
      
      ctx.body = {
        data: responses,
        success: true,
      };
    } catch (error) {
      ctx.body = {
        error: error.message,
        success: false,
      };
    }
  },

  getTraitExpressions: async (ctx) => {
    try {
      const expressions = await strapi.entityService.findMany('api::trait-expression.trait-expression', {
        populate: '*',
      });
      
      ctx.body = {
        data: expressions,
        success: true,
      };
    } catch (error) {
      ctx.body = {
        error: error.message,
        success: false,
      };
    }
  },

  getDailyChallenges: async (ctx) => {
    try {
      const challenges = await strapi.entityService.findMany('api::daily-challenge.daily-challenge', {
        populate: '*',
      });
      
      ctx.body = {
        data: challenges,
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