import { create } from 'zustand';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { Alert } from 'react-native';
import { Platform } from 'react-native';

export type Mode = 'simple' | 'detail';

interface ModeState {
  mode: Mode;
  setMode: (mode: Mode) => Promise<void>;
  hydrate: () => Promise<void>;
}

export const useModeStore = create<ModeState>((set) => ({
  mode: 'simple',
  setMode: async (mode) => {
    const currentMode = useModeStore.getState().mode;
    // シンプル→詳細モードに切り替える時のみマイグレーション実行 (ネイティブのみ)
    if (mode === 'detail' && currentMode === 'simple' && Platform.OS !== 'web') {
      try {
        const { migrateToDetailMode } = await import('../migration/modeMigration');
        await migrateToDetailMode();
      } catch (error) {
        console.error('Migration to detail mode failed:', error);
        // ユーザーにエラーを通知
        Alert.alert('移行エラー', '詳細モードへの移行中にエラーが発生しました。操作は中止されました。');
        // マイグレーション失敗時はモードを変更しない
        return;
      }
    }
    set({ mode });
    await AsyncStorage.setItem('mode', mode);
  },
  hydrate: async () => {
    const saved = await AsyncStorage.getItem('mode');
    if (saved === 'simple' || saved === 'detail') {
      set({ mode: saved });
    }
  },
}));
