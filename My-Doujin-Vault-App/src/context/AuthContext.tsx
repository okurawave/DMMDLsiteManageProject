import React, { createContext, useContext, useEffect } from 'react';
import { useAuthStore } from '../store/authStore';

export type AuthContextType = ReturnType<typeof useAuthStore>;

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const store = useAuthStore();

  // 永続化・自動復元（AsyncStorage等を使う場合はここで実装）
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
