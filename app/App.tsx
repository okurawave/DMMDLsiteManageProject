import { StatusBar } from 'expo-status-bar';
import { StyleSheet } from 'react-native';
import { SafeAreaProvider } from 'react-native-safe-area-context';
import { PaperProvider, Appbar, Button, MD3LightTheme as DefaultTheme } from 'react-native-paper';
import { View, Text } from 'react-native';
import { MaterialCommunityIcons } from '@expo/vector-icons';
import Svg, { Circle } from 'react-native-svg';
import { getShadowStyle, pointerEventsStyle } from './src/ui/styles/shadow';
import { useCounter } from './src/stores/useCounter';
import dayjs from 'dayjs';

export default function App() {
  const { count, inc, dec } = useCounter();
  return (
    <SafeAreaProvider>
      <PaperProvider theme={DefaultTheme}>
        <View style={styles.container}>
          <Appbar.Header style={[getShadowStyle({ elevation: 3 })]}>
            <Appbar.Content title="My App" />
          </Appbar.Header>
          <View style={styles.content}>
            <MaterialCommunityIcons name="hand-wave" size={32} />
            <Text style={styles.title}>Expo 53 + React Native Paper</Text>
            <Svg height={60} width={60}>
              <Circle cx={30} cy={30} r={28} stroke="#6200ee" strokeWidth={3} fill="#bb86fc22" />
            </Svg>
            <Text>Count: {count}</Text>
            <View style={{ flexDirection: 'row', gap: 8 }}>
              <Button mode="outlined" onPress={dec}>-1</Button>
              <Button mode="outlined" onPress={inc}>+1</Button>
            </View>
            <Text>{dayjs().format('YYYY-MM-DD HH:mm:ss')}</Text>
            <Button
              mode="contained"
              onPress={() => {}}
              icon="hand-pointing-right"
              style={pointerEventsStyle('auto')}
            >
              ボタン
            </Button>
          </View>
          <StatusBar style="auto" />
        </View>
      </PaperProvider>
    </SafeAreaProvider>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fff',
  },
  content: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    gap: 16,
    padding: 24,
  },
  title: {
    fontSize: 18,
    marginBottom: 8,
  },
});
