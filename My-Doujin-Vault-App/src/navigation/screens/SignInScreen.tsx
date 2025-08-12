import { Text, View, StyleSheet, Image, useColorScheme, TouchableOpacity, Linking, Alert } from 'react-native';
import { useAuth } from '../../../context/AuthContext';
import { GoogleSignin, statusCodes } from '@react-native-google-signin/google-signin';
import { useEffect } from 'react';

// It's better to manage assets from a central place.
const googleSignInButtonDark = require('../../../assets/google-signin/ios_dark_rd_SI@4x.png');
const googleSignInButtonLight = require('../../../assets/google-signin/ios_light_rd_SI@4x.png');
const appIcon = require('../../../../assets/icon.png');

export function SignInScreen() {
  const { signIn } = useAuth();
  const colorScheme = useColorScheme();
  const isDarkMode = colorScheme === 'dark';

  useEffect(() => {
    GoogleSignin.configure({
      // **************************************************************************************************
      // * IMPORTANT: REPLACE WITH YOUR WEB CLIENT ID FROM GOOGLE CLOUD CONSOLE
      // **************************************************************************************************
      webClientId: 'YOUR_WEB_CLIENT_ID.apps.googleusercontent.com',
      offlineAccess: true,
    });
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
    try {
      await GoogleSignin.hasPlayServices();
      const userInfo = await GoogleSignin.signIn();
      // At this point, you can get the user info from `userInfo`
      // and send it to your backend for verification, etc.
      console.log(JSON.stringify(userInfo, null, 2));
      signIn();
    } catch (error: any) {
      if (error.code === statusCodes.SIGN_IN_CANCELLED) {
        // user cancelled the login flow
        console.log('User cancelled the login flow');
      } else if (error.code === statusCodes.IN_PROGRESS) {
        // operation (e.g. sign in) is in progress already
        console.log('Sign in is in progress');
      } else if (error.code === statusCodes.PLAY_SERVICES_NOT_AVAILABLE) {
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
        <Image source={appIcon} style={styles.logo} />
        <Text style={styles.appName}>My Doujin Vault</Text>
      </View>

      <TouchableOpacity onPress={handleSignIn}>
        <Image source={googleButton} style={styles.signInButton} />
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
