import { create } from 'zustand';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { Platform } from 'react-native';

export type Mode = 'simple' | 'detail';

interface ModeState {
  mode: Mode;
  setMode: (mode: Mode) => void;
  hydrate: () => Promise<void>;
}

export const useModeStore = create<ModeState>((set) => ({
  mode: 'simple',
  setMode: async (mode) => {
    // シンプル→詳細モードに切り替える時のみマイグレーション実行 (ネイティブのみ)
    if (mode === 'detail' && Platform.OS !== 'web') {
      const { migrateToDetailMode } = await import('../migration/modeMigration');
      await migrateToDetailMode();
    }
    set({ mode });
    AsyncStorage.setItem('mode', mode);
  },
  hydrate: async () => {
    const saved = await AsyncStorage.getItem('mode');
    if (saved === 'simple' || saved === 'detail') {
      set({ mode: saved });
    }
  },
}));
