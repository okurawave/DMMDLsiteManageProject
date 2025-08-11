import { useLocalSearchParams, useRouter } from 'expo-router';
import { useEffect, useMemo, useState } from 'react';
import { View, ScrollView, Image, Alert, Platform } from 'react-native';
import { TextInput, Button, ActivityIndicator, Text as PaperText, Card, Snackbar } from 'react-native-paper';
import { getWorkDoc, updateWorkDoc, deleteWorkDoc, uploadWorkCover, ensureSignedInAnonymously } from '../../src/lib/firebase';
import { useWorksStore } from '../../src/stores/works';

export default function WorkDetail() {
  const { id } = useLocalSearchParams<{ id: string }>();
  const router = useRouter();
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [deleting, setDeleting] = useState(false);
  const [snack, setSnack] = useState<string | null>(null);
  const [doc, setDoc] = useState<any | null>(null);
  const getLocal = useWorksStore((s) => s.get);
  const updateLocal = useWorksStore((s) => s.updateLocal);
  const markDeleteLocal = useWorksStore((s) => s.markDeleteLocal);
  const syncToCloud = useWorksStore((s) => s.syncToCloud);
  const [title, setTitle] = useState('');
  const [platform, setPlatform] = useState<string | undefined>('DLsite');
  const [status, setStatus] = useState<string | undefined>('未読');
  const [tags, setTags] = useState<string>('');
  const [coverUrl, setCoverUrl] = useState<string | undefined>('');

  useEffect(() => {
    (async () => {
      try {
        const local = getLocal(id);
        if (local) {
          setDoc(local);
          setTitle(local.title ?? '');
          setPlatform((local as any).platform ?? 'DLsite');
          setStatus((local as any).status ?? '未読');
          setTags(Array.isArray(local.tags) ? local.tags.join(', ') : '');
          setCoverUrl(local.coverImageUrl);
        } else {
          await ensureSignedInAnonymously();
          const d = await getWorkDoc(id);
          setDoc(d);
          setTitle(d?.title ?? '');
          setPlatform(d?.platform ?? 'DLsite');
          setStatus(d?.status ?? '未読');
          setTags(Array.isArray(d?.tags) ? d!.tags.join(', ') : '');
          setCoverUrl(d?.coverImageUrl);
        }
      } catch (e: any) {
        setSnack(e?.message ?? '読み込みに失敗しました');
      } finally {
        setLoading(false);
      }
    })();
  }, [id]);

  const onSave = async () => {
    setSaving(true);
    try {
  const patch = { title, platform, status, tags: tags.split(',').map((t) => t.trim()).filter(Boolean) } as any;
  updateLocal(id, patch);
  setSnack('ローカルに保存しました');
    } catch (e: any) {
      setSnack(e?.message ?? '保存に失敗しました');
    } finally {
      setSaving(false);
    }
  };

  const onDelete = async () => {
    if (Platform.OS === 'web') {
      // eslint-disable-next-line no-alert
      if (!(window as any).confirm?.('この作品を削除しますか？')) return;
    } else {
      let ok = false;
      await new Promise<void>((resolve) => {
        Alert.alert('確認', 'この作品を削除しますか？', [
          { text: 'キャンセル', style: 'cancel', onPress: () => { ok = false; resolve(); } },
          { text: '削除', style: 'destructive', onPress: () => { ok = true; resolve(); } },
        ]);
      });
      if (!ok) return;
    }
    setDeleting(true);
    try {
  markDeleteLocal(id);
  setSnack('ローカルで削除マークしました（同期でクラウドからも削除）');
      router.back();
    } catch (e: any) {
      setSnack(e?.message ?? '削除に失敗しました');
    } finally {
      setDeleting(false);
    }
  };

  const onPickAndUpload = async () => {
    try {
      // URL指定で取得→Storageへアップロード
      // eslint-disable-next-line no-alert
      const src = (globalThis as any).prompt?.('カバー画像のURLを入力（取得してStorageに保存します）:');
      if (!src) return;
      const resp = await fetch(src);
      const blob = await resp.blob();
      const contentType = resp.headers.get('content-type') || 'image/jpeg';
  // 画像はまずURLをdocに保存（後で同期）
  updateLocal(id, { coverImageUrl: URL.createObjectURL(blob), coverSourceUrl: src });
  setCoverUrl(URL.createObjectURL(blob));
  setSnack('カバー画像をローカルに反映しました（同期は別途）');
    } catch (e: any) {
      setSnack(e?.message ?? '画像更新に失敗しました');
    }
  };

  if (loading) {
    return (
      <View style={{ flex: 1, alignItems: 'center', justifyContent: 'center' }}>
        <ActivityIndicator />
        <PaperText style={{ marginTop: 8 }}>読み込み中...</PaperText>
      </View>
    );
  }

  if (!doc) {
    return (
      <View style={{ flex: 1, alignItems: 'center', justifyContent: 'center' }}>
        <PaperText>データが見つかりません</PaperText>
      </View>
    );
  }

  return (
    <ScrollView contentContainerStyle={{ padding: 16, gap: 12 }}>
      <Card>
        <Card.Title title="作品詳細" subtitle={`ID: ${id}`} />
        <Card.Content>
          {coverUrl ? (
            <Image source={{ uri: coverUrl }} style={{ width: '100%', height: 200, marginBottom: 12, borderRadius: 8 }} resizeMode="cover" />
          ) : null}
          <TextInput label="タイトル" value={title} onChangeText={setTitle} style={{ marginBottom: 8 }} />
          <TextInput label="プラットフォーム" value={platform} onChangeText={setPlatform} style={{ marginBottom: 8 }} />
          <TextInput label="ステータス" value={status} onChangeText={setStatus} style={{ marginBottom: 8 }} />
          <TextInput label="タグ（カンマ区切り）" value={tags} onChangeText={setTags} style={{ marginBottom: 8 }} />
          <TextInput label="カバー画像URL" value={coverUrl ?? ''} onChangeText={setCoverUrl} style={{ marginBottom: 8 }} />
          <View style={{ flexDirection: 'row', gap: 8 }}>
            <Button mode="contained" loading={saving} disabled={saving} onPress={onSave}>保存</Button>
            <Button mode="outlined" onPress={onPickAndUpload}>画像アップロード</Button>
            <Button mode="text" textColor="tomato" loading={deleting} disabled={deleting} onPress={onDelete}>削除</Button>
            <Button mode="outlined" onPress={() => syncToCloud().then(() => setSnack('クラウドと同期しました')).catch((e) => setSnack(String(e)))}>同期</Button>
          </View>
        </Card.Content>
      </Card>
      <Snackbar visible={!!snack} onDismiss={() => setSnack(null)} duration={4000}>
        {snack || ''}
      </Snackbar>
    </ScrollView>
  );
}
