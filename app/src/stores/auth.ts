import { create } from 'zustand';
import {
	getAuth,
	GoogleAuthProvider,
	onAuthStateChanged,
	signInWithPopup,
	signInWithEmailAndPassword,
	signOut as fbSignOut,
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

export const useAuthStore = create<AuthState>((set, get) => ({
	user: null,
	startAuthListener: () => {
		const auth = getAuth();
		onAuthStateChanged(auth, (u) => set({ user: u }));
	},
	signInWithGoogle: async () => {
		const auth = getAuth();
		const provider = new GoogleAuthProvider();
		await signInWithPopup(auth, provider);
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
	},
}));
