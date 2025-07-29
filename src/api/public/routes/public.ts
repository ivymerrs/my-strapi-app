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
  ],
}; 