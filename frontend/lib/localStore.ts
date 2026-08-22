'use client';

/*
 * Tiny localStorage-backed external store compatible with
 * useSyncExternalStore (SSR-safe, no hydration mismatch, no cascading
 * renders). Values are cached per raw-string so getSnapshot is referentially
 * stable between renders.
 */

export interface LocalStore<T> {
  subscribe(listener: () => void): () => void;
  get(): T | null;          // imperative read (client only)
  getSnapshot(): T | null;  // for useSyncExternalStore
  getServerSnapshot(): null;
  set(value: T | null): void;
}

export function createLocalStore<T>(
  key: string,
  parse: (raw: string) => T,
  serialize: (value: T) => string = JSON.stringify,
): LocalStore<T> {
  const listeners = new Set<() => void>();
  let cachedRaw: string | null = null;
  let cachedValue: T | null = null;

  function read(): T | null {
    if (typeof window === 'undefined') return null;
    let raw: string | null = null;
    try { raw = localStorage.getItem(key); } catch { /* private mode */ }
    if (raw === cachedRaw) return cachedValue;
    cachedRaw = raw;
    try {
      cachedValue = raw ? parse(raw) : null;
    } catch {
      localStorage.removeItem(key);
      cachedValue = null;
    }
    return cachedValue;
  }

  return {
    subscribe(listener) {
      listeners.add(listener);
      // Cross-tab sync
      window.addEventListener('storage', listener);
      return () => {
        listeners.delete(listener);
        window.removeEventListener('storage', listener);
      };
    },
    get: read,
    getSnapshot: read,
    getServerSnapshot: () => null,
    set(value) {
      try {
        if (value === null) localStorage.removeItem(key);
        else localStorage.setItem(key, serialize(value));
      } catch { /* quota / private mode */ }
      cachedRaw = null; // invalidate cache
      listeners.forEach(l => l());
    },
  };
}
