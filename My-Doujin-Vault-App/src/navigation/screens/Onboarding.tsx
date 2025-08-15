import React from 'react';
import { View, Text, Button, StyleSheet } from 'react-native';
import { useNavigation } from '@react-navigation/native';
import type { NativeStackNavigationProp } from '@react-navigation/native-stack';
import type { AuthStackParamList } from '../index';

export const OnboardingScreen: React.FC = () => {
  const navigation = useNavigation<NativeStackNavigationProp<AuthStackParamList>>();
  const handleStart = () => {
    navigation.navigate('SignIn');
  };
  // TODO: スワイプ形式やページ切り替えUIを追加
  return (
    <View style={styles.container}>
      <Text style={styles.title}>ようこそ My Doujin Vault へ</Text>
      <Text style={styles.text}>Google Drive連携のメリットやプライバシー方針を案内します。</Text>
      {/* TODO: Google認証・権限付与ボタン配置 */}
      <Button title="Googleで認証してはじめる" onPress={handleStart} />
    </View>
  );
};

const styles = StyleSheet.create({
  container: { flex: 1, justifyContent: 'center', alignItems: 'center', padding: 24 },
  title: { fontSize: 24, fontWeight: 'bold', marginBottom: 16 },
  text: { fontSize: 16, marginBottom: 32 },
});
