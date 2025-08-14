import { create } from 'zustand';

export type AuthUser = {
  name: string;
  email: string;
  picture?: string;
};

export type AuthState = {
  isLoggedIn: boolean;
  accessToken: string | null;
  user: AuthUser | null;
  login: (token: string, user: AuthUser) => void;
  logout: () => void;
};

export const useAuthStore = create<AuthState>((set) => ({
  isLoggedIn: false,
  accessToken: null,
  user: null,
  login: (token, user) => set(() => ({ isLoggedIn: true, accessToken: token, user })),
  logout: () => set(() => ({ isLoggedIn: false, accessToken: null, user: null })),
}));
