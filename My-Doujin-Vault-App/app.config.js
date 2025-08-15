import 'dotenv/config';

export default {
  expo: {
    name: 'My-Doujin-Vault-App',
    slug: 'My-Doujin-Vault-App',
    version: '1.0.0',
    orientation: 'default',
    icon: './assets/icon.png',
    userInterfaceStyle: 'automatic',
    newArchEnabled: true,
    scheme: 'mydoujinvaultapp',
    ios: {
      supportsTablet: true,
      bundleIdentifier: 'com.mydoujinvaultapp',
    },
    android: {
      adaptiveIcon: {
        foregroundImage: './assets/adaptive-icon.png',
        backgroundColor: '#ffffff',
      },
      package: 'com.mydoujinvaultapp',
    },
    web: {
      favicon: './assets/favicon.png',
    },
    plugins: [
      [
        'expo-asset',
        {
          assets: ['./assets/google_signin/*.png'],
        },
      ],
      [
        'expo-splash-screen',
        {
          backgroundColor: '#ffffff',
          image: './assets/splash-icon.png',
        },
      ],
      'react-native-edge-to-edge',
      [
        '@react-native-google-signin/google-signin',
        {
          iosUrlScheme: process.env.IOS_URL_SCHEME,
        },
      ],
    ],
    assetBundlePatterns: ['assets/google_signin/*'],
    extra: {
      GOOGLE_WEB_CLIENT_ID: process.env.GOOGLE_WEB_CLIENT_ID,
    },
  },
};
