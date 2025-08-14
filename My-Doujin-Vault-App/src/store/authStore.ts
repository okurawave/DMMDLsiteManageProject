import { create } from 'zustand';

export type AuthState = {
  isLoggedIn: boolean;
  accessToken: string | null;
  user: {
    name: string;
    email: string;
    picture?: string;
  } | null;
  login: (token: string, user: { name: string; email: string; picture?: string }) => void;
  logout: () => void;
};

export const useAuthStore = create<AuthState>((set) => ({
  isLoggedIn: false,
  accessToken: null,
  user: null,
  login: (token: string, user: { name: string; email: string; picture?: string }) => set(() => ({ isLoggedIn: true, accessToken: token, user })),
  logout: () => set(() => ({ isLoggedIn: false, accessToken: null, user: null })),
}));
