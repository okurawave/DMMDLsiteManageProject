import { Stack } from 'expo-router';
import { SafeAreaProvider } from 'react-native-safe-area-context';
import { PaperProvider } from 'react-native-paper';
import { getPaperTheme, useThemeStore } from '../src/theme';

export default function RootLayout() {
  // サブスクライブしてテーマ変更を反映
  const mode = useThemeStore((s) => s.mode);
  return (
    <SafeAreaProvider>
      <PaperProvider theme={getPaperTheme()}>
        <Stack>
          <Stack.Screen name="(tabs)" options={{ headerShown: false }} />
        </Stack>
      </PaperProvider>
    </SafeAreaProvider>
  );
}
