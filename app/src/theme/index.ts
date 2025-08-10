import { MD3DarkTheme, MD3LightTheme, type MD3Theme } from 'react-native-paper';
import { create } from 'zustand';

interface ThemeState {
  mode: 'light' | 'dark';
  toggle: () => void;
}

export const useThemeStore = create<ThemeState>((set, get) => ({
  mode: 'light',
  toggle: () => set({ mode: get().mode === 'light' ? 'dark' : 'light' }),
}));

export function getPaperTheme(): MD3Theme {
  const mode = useThemeStore.getState().mode;
  return mode === 'dark' ? MD3DarkTheme : MD3LightTheme;
}
