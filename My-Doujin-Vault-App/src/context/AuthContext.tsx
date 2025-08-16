import React, { createContext, useContext, useEffect } from 'react';
import { useAuthStore } from '../store/authStore';

import type { AuthState } from '../store/authStore';
export type AuthContextType = AuthState;

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const store = useAuthStore();
  useEffect(() => {
    // TODO: 認証状態の永続化・復元処理
  }, []);
  return <AuthContext.Provider value={store}>{children}</AuthContext.Provider>;
};

export const useAuthContext = () => {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuthContext must be used within AuthProvider');
  return ctx;
};
