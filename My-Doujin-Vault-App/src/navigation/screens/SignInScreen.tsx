import { Text, View, StyleSheet, Image, useColorScheme, TouchableOpacity, Linking, Alert, Platform } from 'react-native';
import { useAuthContext } from '../../context/AuthContext';
import { useEffect } from 'react';
import { useGoogleAuth } from '../../hooks/useGoogleAuth';
export function SignInScreen() {
  // アセットの管理
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

  const { login } = useAuthContext();
  const colorScheme = useColorScheme();
  const isDarkMode = colorScheme === 'dark';
  const { signIn: googleSignIn, user, loading, error } = useGoogleAuth();

  // Google認証成功時にグローバルストアへ反映
  useEffect(() => {
    if (user) {
      login(user.accessToken, {
        name: user.name,
        email: user.email,
        picture: user.picture,
      });
    }
  }, [user, login]);

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

  const handleSignIn = () => {
    googleSignIn();
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

      <TouchableOpacity onPress={handleSignIn} disabled={loading}>
        {loading ? (
          <View style={[styles.signInButton, { justifyContent: 'center', alignItems: 'center', backgroundColor: '#ccc' }]}> 
            <Text style={{ color: '#666', fontSize: 16 }}>Signing in...</Text>
          </View>
        ) : (
          googleButton && Platform.OS !== 'web' ? (
            <Image source={googleButton} style={styles.signInButton} />
          ) : (
            <View style={[styles.signInButton, { backgroundColor: '#4285f4', justifyContent: 'center', alignItems: 'center' }]}> 
              <Text style={{ color: 'white', fontSize: 16, fontWeight: 'bold' }}>
                {Platform.OS === 'web' ? 'Sign in with Google (Web)' : 'Sign in with Google'}
              </Text>
            </View>
          )
        )}
      </TouchableOpacity>

      {error && (
        <Text style={{ color: 'red', marginTop: 10 }}>{error}</Text>
      )}

      {user && (
        <View style={{ marginTop: 20, alignItems: 'center' }}>
          <Text>Welcome, {user.name}</Text>
          <Text style={{ fontSize: 12, color: '#666' }}>{user.email}</Text>
        </View>
      )}

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
