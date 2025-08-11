import { create, type StateCreator } from 'zustand';
import type { Work, WorkCreate } from '@/types/work';
import { addWorkDoc, updateWorkDoc, deleteWorkDoc, ensureSignedInAnonymously } from '@/lib/firebase';

type SyncOptions = {
	mode?: 'push';
};

type WorksState = {
	items: Record<string, Work>; // localId -> Work
	order: string[]; // localId ordering
	lastSyncAt?: number | null;
	addLocal: (data: WorkCreate) => string; // returns local id
	updateLocal: (id: string, patch: Partial<Work>) => void;
	markDeleteLocal: (id: string) => void;
	removeLocal: (id: string) => void;
	list: () => Work[];
	get: (id: string) => Work | undefined;
	syncToCloud: () => Promise<void>;
	setAutoSyncInterval: (ms: number | null) => void;
	_interval?: any;
};

const createId = () => `${Math.random().toString(36).slice(2)}${Date.now().toString(36)}`;

const creator: StateCreator<WorksState> = (set, get) => ({
	items: {},
	order: [],
	lastSyncAt: null,
	addLocal: (data) => {
		const id = createId();
		const now = Date.now();
		const w: Work = {
			id,
			title: data.title,
			platform: data.platform,
			status: data.status,
			tags: data.tags,
			coverSourceUrl: data.coverSourceUrl,
			productUrl: data.productUrl,
			createdAt: now,
			updatedAt: now,
			_dirty: true,
			_syncState: 'pending',
		};
		set((s) => ({ items: { ...s.items, [id]: w }, order: [id, ...s.order] }));
		return id;
	},
	updateLocal: (id, patch) => {
		set((s) => {
			const prev = s.items[id];
			if (!prev) return s as any;
			const next: Work = { ...prev, ...patch, updatedAt: Date.now(), _dirty: true, _syncState: 'pending' };
			return { ...s, items: { ...s.items, [id]: next } };
		});
	},
	markDeleteLocal: (id) => {
			set((s) => {
				const prev = s.items[id];
						if (!prev) {
					const now = Date.now();
							const tomb: Work = { id, remoteId: id, title: '', createdAt: now, updatedAt: now, _deleted: true, _dirty: true, _syncState: 'pending' } as any;
					return { ...s, items: { ...s.items, [id]: tomb } } as any;
				}
				return { ...s, items: { ...s.items, [id]: { ...prev, _deleted: true, _dirty: true, _syncState: 'pending' } } };
			});
	},
	removeLocal: (id) => set((s) => {
		const { [id]: _, ...rest } = s.items;
		return { items: rest, order: s.order.filter((x: string) => x !== id) } as any;
	}),
	list: () => {
		const s = get();
			return s.order
				.map((id: string) => s.items[id])
				.filter((w): w is Work => Boolean(w) && !w._deleted);
	},
	get: (id) => get().items[id],
	syncToCloud: async () => {
		const s = get();
		const dirty = (Object.values(s.items) as Work[]).filter((w) => w._dirty);
		if (!dirty.length) return;
		const user = await ensureSignedInAnonymously();
		for (const w of dirty) {
			try {
				if (w._deleted) {
					if (w.remoteId) await deleteWorkDoc(w.remoteId);
					set((s2) => ({ ...s2, items: { ...s2.items, [w.id]: { ...w, _dirty: false, _syncState: 'synced' } } }));
					continue;
				}
				if (!w.remoteId) {
					const remoteId = await addWorkDoc({
						title: w.title,
						platform: w.platform,
						status: w.status,
						tags: w.tags,
						uid: user?.uid,
						coverImageUrl: w.coverImageUrl,
						productUrl: w.productUrl,
						createdAt: undefined, // serverTimestamp inside addWorkDoc
					});
					set((s2) => ({ ...s2, items: { ...s2.items, [w.id]: { ...w, remoteId, _dirty: false, _syncState: 'synced' } } }));
				} else {
					await updateWorkDoc(w.remoteId as string, {
						title: w.title,
						platform: w.platform,
						status: w.status,
						tags: w.tags,
						coverImageUrl: w.coverImageUrl,
						productUrl: w.productUrl,
					});
					set((s2) => ({ ...s2, items: { ...s2.items, [w.id]: { ...w, _dirty: false, _syncState: 'synced' } } }));
				}
			} catch (e) {
				set((s2) => ({ ...s2, items: { ...s2.items, [w.id]: { ...w, _syncState: 'error' } } }));
			}
		}
		set({ lastSyncAt: Date.now() });
	},
	setAutoSyncInterval: (ms) => {
		const curr = get()._interval;
		if (curr) clearInterval(curr);
		if (!ms) {
			set({ _interval: undefined });
			return;
		}
		const h = setInterval(() => {
			get().syncToCloud().catch(() => {});
		}, ms);
		set({ _interval: h });
	},
});

export const useWorksStore = create<WorksState>()(creator);
