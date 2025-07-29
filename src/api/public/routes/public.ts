export default {
  routes: [
    {
      method: 'GET',
      path: '/public/test',
      handler: 'public.test',
      config: {
        auth: false,
      },
    },
    {
      method: 'GET',
      path: '/public/core-needs',
      handler: 'public.getCoreNeeds',
      config: {
        auth: false,
      },
    },
    {
      method: 'GET',
      path: '/public/personality-traits',
      handler: 'public.getPersonalityTraits',
      config: {
        auth: false,
      },
    },
    {
      method: 'GET',
      path: '/public/dialogue-scenarios',
      handler: 'public.getDialogueScenarios',
      config: {
        auth: false,
      },
    },
    {
      method: 'GET',
      path: '/public/ideal-responses',
      handler: 'public.getIdealResponses',
      config: {
        auth: false,
      },
    },
    {
      method: 'GET',
      path: '/public/responses',
      handler: 'public.getResponses',
      config: {
        auth: false,
      },
    },
    {
      method: 'GET',
      path: '/public/trait-expressions',
      handler: 'public.getTraitExpressions',
      config: {
        auth: false,
      },
    },
    {
      method: 'GET',
      path: '/public/daily-challenges',
      handler: 'public.getDailyChallenges',
      config: {
        auth: false,
      },
    },
  ],
}; 