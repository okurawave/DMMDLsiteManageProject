import { Assets as NavigationAssets } from '@react-navigation/elements';
import { DarkTheme, DefaultTheme } from '@react-navigation/native';
import { Asset } from 'expo-asset';
import { createURL } from 'expo-linking';
import * as SplashScreen from 'expo-splash-screen';
import * as React from 'react';
import { useColorScheme } from 'react-native';
import { Navigation } from './navigation';
import { AuthProvider } from './context/AuthContext';

Asset.loadAsync([
  ...NavigationAssets,
  require('./assets/newspaper.png'),
  require('./assets/bell.png'),
  require('../assets/icon.png'),
  require('./assets/google-signin/ios_dark_rd_SI@4x.png'),
  require('./assets/google-signin/ios_light_rd_SI@4x.png'),
]);

SplashScreen.preventAutoHideAsync();

const prefix = createURL('/');

export function App() {
  const colorScheme = useColorScheme();

  const theme = colorScheme === 'dark' ? DarkTheme : DefaultTheme

  return (
    <AuthProvider>
      <Navigation
        theme={theme}
        linking={{
          enabled: 'auto',
          prefixes: [prefix],
        }}
        onReady={() => {
          SplashScreen.hideAsync();
        }}
      />
    </AuthProvider>
  );
}
