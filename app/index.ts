import '@expo/metro-runtime';
import { registerRootComponent } from 'expo';

import App from './App';

// Dev-only: filter noisy RN Web deprecation warnings
if (process.env.NODE_ENV === 'development') {
	const originalWarn = console.warn;
	console.warn = (...args: unknown[]) => {
		const msg = String(args[0] ?? '');
		if (
			msg.includes('props.pointerEvents is deprecated') ||
			msg.includes('"shadow*" style props are deprecated')
		) {
			return;
		}
		originalWarn(...(args as unknown[]));
	};
}

// registerRootComponent calls AppRegistry.registerComponent('main', () => App);
// It also ensures that whether you load the app in Expo Go or in a native build,
// the environment is set up appropriately
registerRootComponent(App);
