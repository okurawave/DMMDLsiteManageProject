import { View, Text, StyleSheet, FlatList } from 'react-native';
import { Searchbar, Card, Button, ActivityIndicator, Text as PaperText, FAB, Chip, Snackbar } from 'react-native-paper';
import { useState, useMemo, useEffect } from 'react';
import FadeInView from '../../src/components/FadeInView';
import Animated, { useSharedValue, useAnimatedStyle, withTiming } from 'react-native-reanimated';
import { ensureSignedInAnonymously, listWorkDocs, addWorkDoc, subscribeWorks, listWorksPage, tryExtractIndexUrlFromError } from '../../src/lib/firebase';
import * as Linking from 'expo-linking';
import dayjs from 'dayjs';
import relativeTime from 'dayjs/plugin/relativeTime';
import 'dayjs/locale/ja';
dayjs.locale('ja');
dayjs.extend(relativeTime);
import { useRouter, useFocusEffect } from 'expo-router';
import { useCallback } from 'react';

const MOCK = Array.from({ length: 12 }).map((_, i) => ({ id: String(i + 1), title: `作品 ${i + 1}` }));

export default function Library() {
		const [q, setQ] = useState('');
			const [remote, setRemote] = useState<Array<{ id: string; title?: string; platform?: string; status?: string; tags?: string[]; createdAt?: any }>>([]);
			const [loading, setLoading] = useState(false);
			const [error, setError] = useState<string | null>(null);
			const [snack, setSnack] = useState<string | null>(null);
			const [platformFilter, setPlatformFilter] = useState<string | null>(null);
			const [statusFilter, setStatusFilter] = useState<string | null>(null);
			const [tagFilter, setTagFilter] = useState<string | null>(null);
			const [sortDesc, setSortDesc] = useState(true);
			const [lastDoc, setLastDoc] = useState<any>(null);
			const [uid, setUid] = useState<string | null>(null);
			const [appending, setAppending] = useState(false);
			const ids = useMemo(() => new Set(remote.map(r => r.id)), [remote]);
		const data = useMemo(() => {
			const base = remote.length ? remote : MOCK;
			return base.filter((x) => (x.title ?? '').includes(q));
		}, [q, remote]);

		const load = useCallback(async () => {
			setLoading(true);
			setError(null);
			try {
				const user = await ensureSignedInAnonymously();
				setUid(user?.uid ?? null);
				// 初回はリアルタイム購読
				const unsub = subscribeWorks(
					{
						uid: user?.uid ?? undefined,
						platform: platformFilter ?? undefined,
						status: statusFilter ?? undefined,
						tag: tagFilter ?? undefined,
						sort: sortDesc ? 'createdAt_desc' : 'createdAt_asc',
						limit: 10,
					},
									(items, last) => {
						setRemote(items as any);
						setLastDoc(last);
										},
										(err) => {
											const url = tryExtractIndexUrlFromError(err);
											if (url) setSnack(`インデックスが必要です。開く: ${url}`);
											else setError(err?.message ?? '購読エラーが発生しました');
										}
				);
				return () => unsub();
			} catch (e: any) {
				console.warn(e);
				setError(e?.message ?? '読み込みに失敗しました');
			} finally {
				setLoading(false);
			}
		}, [platformFilter, statusFilter, tagFilter, sortDesc]);

		useEffect(() => {
			let unsub: undefined | (() => void);
			(async () => {
				const maybeUnsub = await load();
				if (typeof maybeUnsub === 'function') unsub = maybeUnsub;
			})();
			return () => { if (unsub) unsub(); };
		}, [load]);

		useFocusEffect(
			useCallback(() => {
				load();
			}, [load])
		);
	const router = useRouter();
	return (
		<View style={styles.container}>
			<Searchbar value={q} onChangeText={setQ} placeholder="検索" style={{ margin: 12 }} />
			<View style={{ flexDirection: 'row', flexWrap: 'wrap', gap: 8, paddingHorizontal: 12 }}>
				<Chip selected={!platformFilter} onPress={() => setPlatformFilter(null)}>全プラットフォーム</Chip>
				<Chip selected={platformFilter === 'DLsite'} onPress={() => setPlatformFilter('DLsite')}>DLsite</Chip>
				<Chip selected={platformFilter === 'Fanza'} onPress={() => setPlatformFilter('Fanza')}>Fanza</Chip>
				<Chip selected={platformFilter === 'その他'} onPress={() => setPlatformFilter('その他')}>その他</Chip>
			</View>
			<View style={{ flexDirection: 'row', flexWrap: 'wrap', gap: 8, paddingHorizontal: 12, marginTop: 8 }}>
				<Chip selected={!statusFilter} onPress={() => setStatusFilter(null)}>全ステータス</Chip>
				<Chip selected={statusFilter === '未読'} onPress={() => setStatusFilter('未読')}>未読</Chip>
				<Chip selected={statusFilter === 'プレイ中'} onPress={() => setStatusFilter('プレイ中')}>プレイ中</Chip>
				<Chip selected={statusFilter === '読了'} onPress={() => setStatusFilter('読了')}>読了</Chip>
				<Chip selected={statusFilter === '積読'} onPress={() => setStatusFilter('積読')}>積読</Chip>
				<Chip selected={!sortDesc} onPress={() => setSortDesc(!sortDesc)}>{sortDesc ? '新しい順' : '古い順'}</Chip>
			</View>
			<View style={{ flexDirection: 'row', gap: 8, alignItems: 'center', paddingHorizontal: 12, marginTop: 8 }}>
				<Text>タグ:</Text>
				<Searchbar value={tagFilter ?? ''} onChangeText={(v) => setTagFilter(v || null)} placeholder="タグ名" style={{ flex: 1 }} />
			</View>
					{loading && (
						<View style={{ padding: 24, alignItems: 'center' }}>
							<ActivityIndicator />
							<PaperText style={{ marginTop: 8 }}>読み込み中...</PaperText>
						</View>
					)}
					{error && (
						<PaperText style={{ color: 'tomato', marginHorizontal: 12 }}>{error}</PaperText>
					)}
					<FlatList
				data={data}
				keyExtractor={(item) => item.id}
				contentContainerStyle={{ padding: 12, gap: 12 }}
					renderItem={({ item }) => <LibraryItem item={item} />}
								ListEmptyComponent={
									!loading
										? (
											<View style={{ padding: 24, alignItems: 'center' }}>
												<PaperText>データがありません</PaperText>
											</View>
										)
										: null
								}
			/>
					<Button
						mode="contained"
						style={{ margin: 12 }}
						onPress={async () => {
							try {
								const user = await ensureSignedInAnonymously();
								const id = await addWorkDoc({ title: `作品 ${Date.now()}`, uid: user?.uid, platform: 'DLsite', status: '未読', tags: ['sample'] });
								const docs = await listWorkDocs();
								setRemote(docs as any);
							} catch (e) {
								console.warn(e);
								setSnack('作成に失敗しました');
							}
						}}
					>
						作品を追加（Firestore）
					</Button>
				<Button
					mode="outlined"
					style={{ marginHorizontal: 12, marginBottom: 12 }}
					onPress={async () => {
						if (appending || !lastDoc) return;
						setAppending(true);
						try {
							const page = await listWorksPage({
								uid: uid ?? undefined,
								platform: platformFilter ?? undefined,
								status: statusFilter ?? undefined,
								tag: tagFilter ?? undefined,
								sort: sortDesc ? 'createdAt_desc' : 'createdAt_asc',
								limit: 10,
								cursor: lastDoc,
							});
							const merged = [...remote];
							for (const it of page.items as any[]) {
								if (!ids.has(it.id)) merged.push(it);
							}
							setRemote(merged as any);
							setLastDoc(page.lastDoc);
						} catch (e) {
							console.warn(e);
							setSnack('読み込みに失敗しました');
						} finally {
							setAppending(false);
						}
					}}
				>
					さらに読み込む
				</Button>
				<FAB
					icon="plus"
					style={{ position: 'absolute', right: 16, bottom: 16 }}
					onPress={() => router.push('/add')}
				/>
							<Snackbar
								visible={!!snack || !!error}
								onDismiss={() => { setSnack(null); setError(null); }}
								duration={6000}
								action={(() => {
									const url = snack && snack.includes('http') ? snack.split(' ').pop() : null;
									if (url) return { label: '開く', onPress: () => Linking.openURL(url as string) };
									return undefined as any;
								})()}
							>
								{snack || error || ''}
							</Snackbar>
		</View>
	);
}

const styles = StyleSheet.create({
	container: { flex: 1 },
});

function LibraryItem({ item }: { item: { id: string; title?: string; createdAt?: any; platform?: string; status?: string; tags?: string[] } }) {
	const scale = useSharedValue(1);
	const aStyle = useAnimatedStyle(() => ({ transform: [{ scale: scale.value }] }));
	const subtitle = (() => {
		const ts = item.createdAt;
		if (!ts) return `ID: ${item.id}`;
		// Firestore Timestamp or {seconds,nanoseconds}
		const ms = ts?.toDate ? ts.toDate().getTime() : (typeof ts.seconds === 'number' ? ts.seconds * 1000 : Date.now());
		const meta: string[] = [];
		if (item.platform) meta.push(item.platform);
		if (item.status) meta.push(item.status);
		const metaStr = meta.length ? `｜${meta.join(' / ')}` : '';
		return `${dayjs(ms).fromNow()}${metaStr}｜ID: ${item.id}`;
	})();
	return (
		<FadeInView>
			<Animated.View style={aStyle}>
				<Card
					onPressIn={() => { scale.value = withTiming(0.98, { duration: 80 }); }}
					onPressOut={() => { scale.value = withTiming(1, { duration: 120 }); }}
				>
					<Card.Title title={item.title} subtitle={subtitle} />
					<Card.Content>
						{Array.isArray(item.tags) && item.tags.length > 0 ? (
							<View style={{ flexDirection: 'row', flexWrap: 'wrap', gap: 6 }}>
								{item.tags.map((t) => (
									<Chip key={t} compact>{t}</Chip>
								))}
							</View>
						) : (
							<Text>説明文（ダミー）</Text>
						)}
					</Card.Content>
				</Card>
			</Animated.View>
		</FadeInView>
	);
}