import React from 'react';
import { View, Text, Button, StyleSheet } from 'react-native';

export const OnboardingScreen: React.FC<{ onFinish?: () => void }> = ({ onFinish = () => {} }) => {
  // TODO: スワイプ形式やページ切り替えUIを追加
  return (
    <View style={styles.container}>
      <Text style={styles.title}>ようこそ My Doujin Vault へ</Text>
      <Text style={styles.text}>Google Drive連携のメリットやプライバシー方針を案内します。</Text>
      {/* TODO: Google認証・権限付与ボタン配置 */}
      <Button title="Googleで認証してはじめる" onPress={onFinish} />
    </View>
  );
};

const styles = StyleSheet.create({
  container: { flex: 1, justifyContent: 'center', alignItems: 'center', padding: 24 },
  title: { fontSize: 24, fontWeight: 'bold', marginBottom: 16 },
  text: { fontSize: 16, marginBottom: 32 },
});
