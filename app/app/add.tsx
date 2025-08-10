import { View, StyleSheet } from 'react-native';
import { TextInput, Button, Snackbar, HelperText, Chip } from 'react-native-paper';
import { useState } from 'react';
import { addWorkDoc, ensureSignedInAnonymously } from '../src/lib/firebase';
import { useRouter } from 'expo-router';

export default function AddWork() {
  const [title, setTitle] = useState('');
  const [platform, setPlatform] = useState<'DLsite' | 'Fanza' | 'その他'>('DLsite');
  const [status, setStatus] = useState<'未読' | '読了' | 'プレイ中' | '積読'>('未読');
  const [tags, setTags] = useState<string>('');
  const [loading, setLoading] = useState(false);
  const [msg, setMsg] = useState<string | null>(null);
  const router = useRouter();
  return (
    <View style={styles.container}>
      <TextInput label="タイトル" value={title} onChangeText={setTitle} style={{ margin: 12 }} />
      <HelperText type={title.trim() ? 'info' : 'error'} visible>
        タイトルは必須です
      </HelperText>
      <View style={{ flexDirection: 'row', flexWrap: 'wrap', gap: 8, marginHorizontal: 12 }}>
        <Chip selected={platform === 'DLsite'} onPress={() => setPlatform('DLsite')}>DLsite</Chip>
        <Chip selected={platform === 'Fanza'} onPress={() => setPlatform('Fanza')}>Fanza</Chip>
        <Chip selected={platform === 'その他'} onPress={() => setPlatform('その他')}>その他</Chip>
      </View>
      <View style={{ flexDirection: 'row', flexWrap: 'wrap', gap: 8, marginHorizontal: 12, marginTop: 8 }}>
        <Chip selected={status === '未読'} onPress={() => setStatus('未読')}>未読</Chip>
        <Chip selected={status === 'プレイ中'} onPress={() => setStatus('プレイ中')}>プレイ中</Chip>
        <Chip selected={status === '読了'} onPress={() => setStatus('読了')}>読了</Chip>
        <Chip selected={status === '積読'} onPress={() => setStatus('積読')}>積読</Chip>
      </View>
      <TextInput
        label="タグ（カンマ区切り）"
        value={tags}
        onChangeText={setTags}
        style={{ margin: 12 }}
        placeholder="rpg, ドット, 体験版 など"
      />
      <Button
        mode="contained"
        disabled={!title.trim() || loading}
        onPress={async () => {
          setLoading(true);
          try {
            const user = await ensureSignedInAnonymously();
            const tagsArr = tags
              .split(',')
              .map((t) => t.trim())
              .filter((t) => t.length > 0);
            await addWorkDoc({ title: title.trim(), platform, status, tags: tagsArr, uid: user?.uid });
            setMsg('登録しました');
            router.back();
          } catch (e) {
            setMsg('登録に失敗しました');
            console.warn(e);
          } finally {
            setLoading(false);
          }
        }}
        style={{ margin: 12 }}
      >
        登録
      </Button>
      <Snackbar visible={!!msg} onDismiss={() => setMsg(null)} duration={2000}>
        {msg}
      </Snackbar>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, paddingTop: 20 },
});
