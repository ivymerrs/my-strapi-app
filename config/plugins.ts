export default () => ({
  // Completely disable upload plugin to avoid sharp dependency
  upload: {
    enabled: false,
    config: {
      provider: null,
    },
  },
});
