import { Text, View, StyleSheet, Image, useColorScheme, TouchableOpacity, Linking, Alert, Platform } from 'react-native';
import { useAuth } from '../../context/AuthContext';
import { useEffect } from 'react';

// Conditional import for Google Sign-in (only for native platforms)
let GoogleSignin: any = null;
let statusCodes: any = null;

if (Platform.OS !== 'web') {
  try {
    const googleSigninModule = require('@react-native-google-signin/google-signin');
    GoogleSignin = googleSigninModule.GoogleSignin;
    statusCodes = googleSigninModule.statusCodes;
  } catch (e) {
    console.warn('Google Sign-in module not available');
  }
}

// It's better to manage assets from a central place.
let googleSignInButtonDark: any = null;
let googleSignInButtonLight: any = null;
let appIcon: any = null;

if (Platform.OS !== 'web') {
  try {
    googleSignInButtonDark = require('../../assets/google_signin/dark.png');
    googleSignInButtonLight = require('../../assets/google_signin/ios_light_rd_SI@4x.png');
    appIcon = require('../../../assets/icon.png');
  } catch (e) {
    console.warn('Assets not available:', e);
  }
}

export function SignInScreen() {
  const { signIn } = useAuth();
  const colorScheme = useColorScheme();
  const isDarkMode = colorScheme === 'dark';

  useEffect(() => {
    if (Platform.OS !== 'web' && GoogleSignin) {
      GoogleSignin.configure({
        // **************************************************************************************************
        // * IMPORTANT: REPLACE WITH YOUR WEB CLIENT ID FROM GOOGLE CLOUD CONSOLE
        // **************************************************************************************************
        webClientId: 'YOUR_WEB_CLIENT_ID.apps.googleusercontent.com',
        offlineAccess: true,
      });
    }
  }, []);

  const styles = StyleSheet.create({
    container: {
      flex: 1,
      justifyContent: 'center',
      alignItems: 'center',
      backgroundColor: isDarkMode ? '#1C1C1E' : '#F2F2F7',
    },
    headerContainer: {
      position: 'absolute',
      top: 80,
      alignItems: 'center',
    },
    logo: {
      width: 100,
      height: 100,
    },
    appName: {
      fontSize: 24,
      fontWeight: 'bold',
      marginTop: 10,
      color: isDarkMode ? '#FFFFFF' : '#000000',
    },
    signInButton: {
      width: 230, // As per google guidelines, but we can adjust
      height: 56, // As per google guidelines
    },
    footerContainer: {
      position: 'absolute',
      bottom: 40,
      flexDirection: 'row',
      justifyContent: 'space-around',
      width: '80%',
    },
    footerLink: {
      color: isDarkMode ? '#999999' : '#666666',
      textDecorationLine: 'underline',
    },
  });

  const googleButton = isDarkMode ? googleSignInButtonDark : googleSignInButtonLight;

  const handleSignIn = async () => {
    if (Platform.OS === 'web') {
      // For web, use a simple mock sign-in
      Alert.alert('Web Sign-in', 'Google Sign-in is not available on web. Using mock sign-in.', [
        { text: 'OK', onPress: () => signIn() }
      ]);
      return;
    }

    if (!GoogleSignin) {
      Alert.alert('Error', 'Google Sign-in is not available');
      return;
    }

    try {
      await GoogleSignin.hasPlayServices();
      const userInfo = await GoogleSignin.signIn();
      // At this point, you can get the user info from `userInfo`
      // and send it to your backend for verification, etc.
      console.log(JSON.stringify(userInfo, null, 2));
      signIn();
    } catch (error: any) {
      if (statusCodes && error.code === statusCodes.SIGN_IN_CANCELLED) {
        // user cancelled the login flow
        console.log('User cancelled the login flow');
      } else if (statusCodes && error.code === statusCodes.IN_PROGRESS) {
        // operation (e.g. sign in) is in progress already
        console.log('Sign in is in progress');
      } else if (statusCodes && error.code === statusCodes.PLAY_SERVICES_NOT_AVAILABLE) {
        // play services not available or outdated
        Alert.alert('Error', 'Play services not available or outdated');
      } else {
        // some other error happened
        Alert.alert('Error', 'An unknown error occurred during sign-in.');
        console.error(error);
      }
    }
  };

  const openLink = (url: string) => {
    Linking.openURL(url).catch(err => console.error("Couldn't load page", err));
  };

  return (
    <View style={styles.container}>
      <View style={styles.headerContainer}>
        {appIcon && <Image source={appIcon} style={styles.logo} />}
        <Text style={styles.appName}>My Doujin Vault</Text>
      </View>

      <TouchableOpacity onPress={handleSignIn}>
        {googleButton && Platform.OS !== 'web' ? (
          <Image source={googleButton} style={styles.signInButton} />
        ) : (
          <View style={[styles.signInButton, { backgroundColor: '#4285f4', justifyContent: 'center', alignItems: 'center' }]}>
            <Text style={{ color: 'white', fontSize: 16, fontWeight: 'bold' }}>
              {Platform.OS === 'web' ? 'Sign in with Google (Web)' : 'Sign in with Google'}
            </Text>
          </View>
        )}
      </TouchableOpacity>

      <View style={styles.footerContainer}>
        <Text style={styles.footerLink} onPress={() => openLink('https://example.com/privacy')}>
          Privacy Policy
        </Text>
        <Text style={styles.footerLink} onPress={() => openLink('https://example.com/terms')}>
          Terms of Service
        </Text>
      </View>
    </View>
  );
}
