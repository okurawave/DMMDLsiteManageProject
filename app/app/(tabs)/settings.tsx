import { View, Text, StyleSheet } from 'react-native';
import { Switch, List, Button, Card, TextInput } from 'react-native-paper';
import { useThemeStore } from '../../src/theme';
import { useEffect, useState } from 'react';
import { initFirebase, signInWithGoogleWeb, subscribeAuth, signOutUser } from '../../src/lib/firebase';
import { useWorksStore } from '../../src/stores/works';

export default function SettingsTab() {
  const setAutoSyncInterval = useWorksStore((s) => s.setAutoSyncInterval);
  const [syncMinutes, setSyncMinutes] = useState<string>('');
  const mode = useThemeStore((s) => s.mode);
  const toggle = useThemeStore((s) => s.toggle);
  const [userEmail, setUserEmail] = useState<string | null>(null);

  useEffect(() => {
    let unsub: undefined | (() => void);
    try {
      initFirebase();
      unsub = subscribeAuth((u) => setUserEmail(u?.email ?? null));
    } catch {}
    return () => {
      if (unsub) unsub();
    };
  }, []);

  return (
    <View style={styles.container}>
      <Text style={styles.title}>設定</Text>
      <List.Section>
        <List.Item
          title="ダークモード"
          right={() => (
            <Switch value={mode === 'dark'} onValueChange={toggle} />
          )}
        />
        <List.Subheader>認証</List.Subheader>
        <List.Item
          title={userEmail ? `ログイン中: ${userEmail}` : '未ログイン'}
          right={() => (
            userEmail ? (
              <Button onPress={async () => { await signOutUser(); }}>ログアウト</Button>
            ) : (
              <Button onPress={async () => { try { await signInWithGoogleWeb(); } catch (e) { console.warn(e); } }}>Googleでログイン</Button>
            )
          )}
        />
        <List.Item
          title="Firebase 初期化(テスト)"
          description="app.config.ts で環境変数(EXPO_PUBLIC_FIREBASE_*)を設定してください。"
          onPress={async () => {
            try {
              const inited = initFirebase();
              alert(inited ? `Firebase initialized: ${inited.app.name}` : '未設定です');
            } catch (e) {
              console.warn(e);
              alert('初期化に失敗しました。設定ファイルを確認してください。');
            }
          }}
        />
      </List.Section>
      <Card style={{ margin: 12 }}>
        <Card.Title title="同期設定" />
        <Card.Content>
          <TextInput
            label="自動同期（分）"
            value={syncMinutes}
            onChangeText={setSyncMinutes}
            keyboardType="numeric"
            style={{ marginBottom: 8 }}
            placeholder="例: 5"
          />
          <Button
            mode="outlined"
            onPress={() => {
              const m = parseInt(syncMinutes || '0', 10);
              if (!m || m <= 0) {
                setAutoSyncInterval(null);
              } else {
                setAutoSyncInterval(m * 60 * 1000);
              }
            }}
          >
            設定を適用
          </Button>
        </Card.Content>
      </Card>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, alignItems: 'center', justifyContent: 'center', gap: 12 },
  title: { fontSize: 22, fontWeight: '600' },
});
