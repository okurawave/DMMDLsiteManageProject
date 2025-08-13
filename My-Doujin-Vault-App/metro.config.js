const { getDefaultConfig } = require('expo/metro-config');

/** @type {import('expo/metro-config').MetroConfig} */
const config = getDefaultConfig(__dirname);

// Add custom asset extensions if needed
config.resolver.assetExts.push(
  // Add any custom asset extensions here
);

// Enable debug mode for asset resolution troubleshooting
config.resolver.platforms = ['ios', 'android', 'native', 'web'];

module.exports = config;
