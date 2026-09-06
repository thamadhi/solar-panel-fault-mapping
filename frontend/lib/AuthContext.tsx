'use client';

import React, { createContext, useContext, useCallback, useEffect, useSyncExternalStore } from 'react';
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

/**
 * Reads the `exp` claim out of a JWT — no library needed, just the standard
 * base64url-decode of its middle segment. The token itself lives in
 * localStorage (not sessionStorage), so it already survives closing the tab
 * or the whole browser; this is what makes that persistence actually expire
 * instead of lasting forever once issued.
 */
function getTokenExpiryMs(token: string): number | null {
  try {
    const payload = token.split('.')[1];
    const json = atob(payload.replace(/-/g, '+').replace(/_/g, '/'));
    const exp = JSON.parse(json)?.exp;
    return typeof exp === 'number' ? exp * 1000 : null;
  } catch {
    return null;
  }
}

function isExpired(token: string): boolean {
  const expMs = getTokenExpiryMs(token);
  return expMs !== null && Date.now() >= expMs;
}

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

  // A token that outlived its own `exp` doesn't count as logged in, even
  // though it's still sitting in localStorage.
  const valid = !!token && !isExpired(token);

  // Clean up a stale token in the background rather than during render.
  useEffect(() => {
    if (token && !valid) logout();
  }, [token, valid, logout]);

  // Catch expiry that happens while the tab is just sitting open and idle
  // (no API call around to trigger the 401 path in api.ts) by polling.
  useEffect(() => {
    if (!token) return;
    const id = setInterval(() => {
      if (isExpired(token)) logout();
    }, 60_000);
    return () => clearInterval(id);
  }, [token, logout]);

  return (
    <AuthContext.Provider value={{ user, token, isAuthenticated: valid, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}
