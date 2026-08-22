'use client';

import React, { createContext, useContext, useCallback, useSyncExternalStore } from 'react';
import { createLocalStore } from './localStore';

interface User {
  id: number;
  username: string;
  email: string;
  type: string;
}

interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  login: (token: string, user: User) => void;
  logout: () => void;
}

const userStore = createLocalStore<User>('pv_user', JSON.parse);
// Token is stored as a bare string (api.ts reads it directly), so keep the
// legacy format on write and accept both bare and quoted values on read.
const tokenStore = createLocalStore<string>(
  'pv_token',
  (raw) => (raw.startsWith('"') ? JSON.parse(raw) : raw),
  (t) => t,
);

const AuthContext = createContext<AuthState>({
  user: null,
  token: null,
  isAuthenticated: false,
  login: () => {},
  logout: () => {},
});

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const user = useSyncExternalStore(userStore.subscribe, userStore.getSnapshot, userStore.getServerSnapshot);
  const token = useSyncExternalStore(tokenStore.subscribe, tokenStore.getSnapshot, tokenStore.getServerSnapshot);

  const login = useCallback((newToken: string, newUser: User) => {
    tokenStore.set(newToken);
    userStore.set(newUser);
  }, []);

  const logout = useCallback(() => {
    tokenStore.set(null);
    userStore.set(null);
  }, []);

  return (
    <AuthContext.Provider value={{ user, token, isAuthenticated: !!token, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}
