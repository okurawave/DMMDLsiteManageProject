import { create } from 'zustand';
// AsyncStorage (Native) or fallback (Web)
let AsyncStorage: {
  getItem(key: string): Promise<string | null>;
  setItem(key: string, value: string): Promise<void>;
  removeItem(key: string): Promise<void>;
};
try {
  // eslint-disable-next-line @typescript-eslint/no-var-requires
  AsyncStorage = require('@react-native-async-storage/async-storage').default;
} catch {
  // Fallback to localStorage for web dev environments
  const ls = typeof window !== 'undefined' && window.localStorage ? window.localStorage : undefined;
  AsyncStorage = {
    async getItem(k) { return ls ? ls.getItem(k) : null; },
    async setItem(k, v) { if (ls) ls.setItem(k, v); },
    async removeItem(k) { if (ls) ls.removeItem(k); },
  };
}
import {
  getAuth,
  GoogleAuthProvider,
  onAuthStateChanged,
  signInWithPopup,
  signInWithEmailAndPassword,
  signOut as fbSignOut,
  setPersistence,
  browserLocalPersistence,
  signInWithRedirect,
  getRedirectResult,
  type User,
} from 'firebase/auth';
import { initFirebase } from '@/lib/firebase';

interface AuthState {
	user: User | null;
	startAuthListener: () => void;
	signInWithGoogle: () => Promise<void>;
	signInWithEmailDemo: () => Promise<void>;
	signOut: () => Promise<void>;
}

const useAuthStore = create<AuthState>((set, get) => ({
  user: null,
  startAuthListener: () => {
    // 必ず初期化
    try { initFirebase(); } catch {}
    const auth = getAuth();
    if (typeof window !== 'undefined' && setPersistence && browserLocalPersistence) {
      setPersistence(auth, browserLocalPersistence).catch(() => {});
      // localStorageからuserを復元
      AsyncStorage.getItem('authUser').then((val) => {
        if (val) {
          try {
            const user = JSON.parse(val);
            set({ user });
          } catch {}
        }
      });
    }
    // リダイレクトの結果を回収（失敗は握りつぶし）
    getRedirectResult(auth).catch(() => {});
    onAuthStateChanged(auth, (u) => {
      set({ user: u });
      // WebのみlocalStorageに保存
      if (typeof window !== 'undefined') {
        if (u) {
          AsyncStorage.setItem('authUser', JSON.stringify(u));
        } else {
          AsyncStorage.removeItem('authUser');
        }
      }
    });
  },
  signInWithGoogle: async () => {
    try { initFirebase(); } catch {}
    const auth = getAuth();
    const provider = new GoogleAuthProvider();
    if (typeof window !== 'undefined' && (window as any).crossOriginIsolated) {
      await signInWithRedirect(auth, provider);
      return;
    }
    try {
      await signInWithPopup(auth, provider);
    } catch (e: any) {
      const code: string | undefined = e?.code;
      const coopBlocked = typeof (globalThis as any).crossOriginIsolated !== 'undefined' && (globalThis as any).crossOriginIsolated;
      const shouldRedirect = coopBlocked ||
        code === 'auth/operation-not-supported-in-this-environment' ||
        code === 'auth/popup-blocked' ||
        code === 'auth/popup-closed-by-user' ||
        code === 'auth/unauthorized-domain' ||
        code === 'auth/auth-domain-config-required';
      if (shouldRedirect) {
        await signInWithRedirect(auth, provider);
        return;
      }
      throw e;
    }
  },
  signInWithEmailDemo: async () => {
    const auth = getAuth();
    const email = (process.env.EXPO_PUBLIC_DEMO_EMAIL as string) ?? 'demo@example.com';
    const password = (process.env.EXPO_PUBLIC_DEMO_PASSWORD as string) ?? 'password123';
    await signInWithEmailAndPassword(auth, email, password);
  },
  signOut: async () => {
    const auth = getAuth();
    await fbSignOut(auth);
    try {
      await AsyncStorage.removeItem('authUser');
    } catch {}
  },
}));

export { useAuthStore };
