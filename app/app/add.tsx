import { View, StyleSheet, Image, Platform } from 'react-native';
import * as ImagePicker from 'expo-image-picker';
import { TextInput, Button, Snackbar, HelperText, Chip } from 'react-native-paper';
import { useState } from 'react';
// ローカルに追加し、後で同期
import { useWorksStore } from '../src/stores/works';
import { useRouter } from 'expo-router';

export default function AddWork() {
  const addLocal = useWorksStore((s) => s.addLocal);
  const [title, setTitle] = useState('');
  const [platform, setPlatform] = useState<'DLsite' | 'Fanza' | 'その他'>('DLsite');
  const [status, setStatus] = useState<'未読' | '読了' | 'プレイ中' | '積読'>('未読');
  const [tags, setTags] = useState<string>('');
  const [coverUrl, setCoverUrl] = useState('');
  const [coverBlob, setCoverBlob] = useState<Blob | null>(null);
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
      <TextInput
        label="カバー画像URL"
        value={coverUrl}
        onChangeText={setCoverUrl}
        style={{ margin: 12 }}
        placeholder="https://...jpg"
      />
      <Button
        mode="outlined"
        style={{ marginHorizontal: 12, marginBottom: 8 }}
        onPress={async () => {
          let result;
          if (Platform.OS === 'web') {
            result = await ImagePicker.launchImageLibraryAsync({ mediaTypes: ImagePicker.MediaTypeOptions.Images, quality: 0.9 });
            if (result.canceled || !result.assets?.length) return;
            const asset = result.assets[0];
            setCoverUrl(asset.uri);
            const blob = await (await fetch(asset.uri)).blob();
            setCoverBlob(blob);
          } else {
            result = await ImagePicker.launchImageLibraryAsync({ mediaTypes: ImagePicker.MediaTypeOptions.Images, quality: 0.9 });
            if (result.canceled || !result.assets?.length) return;
            const asset = result.assets[0];
            setCoverUrl(asset.uri);
            // Native: Blob取得はFileSystem経由が必要な場合あり（ここではURLのみ保存）
            setCoverBlob(null);
          }
        }}
      >画像を選択</Button>
      {coverUrl ? (
        <Image source={{ uri: coverUrl }} style={{ width: '100%', height: 180, marginBottom: 12, borderRadius: 8 }} resizeMode="cover" />
      ) : null}
      <Button
        mode="contained"
        disabled={!title.trim() || loading}
        onPress={() => {
          setLoading(true);
          const tagsArr = tags
            .split(',')
            .map((t) => t.trim())
            .filter((t) => t.length > 0);
          const id = addLocal({ title: title.trim(), platform, status, tags: tagsArr, coverSourceUrl: coverUrl });
          setMsg('ローカルに追加しました');
          setLoading(false);
          router.replace(`/work/${id}`);
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
