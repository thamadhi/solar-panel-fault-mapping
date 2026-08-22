'use client';

import { useCallback, useSyncExternalStore } from 'react';

type Theme = 'light' | 'dark';

const THEME_KEY = 'pv_theme';

/* The single source of truth is the data-theme attribute on <html>, applied
 * before first paint by THEME_INIT_SCRIPT. Components subscribe via
 * useSyncExternalStore — no cascading setState effects. */

const listeners = new Set<() => void>();

function subscribe(listener: () => void) {
  listeners.add(listener);
  return () => { listeners.delete(listener); };
}

function getSnapshot(): Theme {
  return document.documentElement.getAttribute('data-theme') === 'dark' ? 'dark' : 'light';
}

function getServerSnapshot(): Theme {
  return 'light';
}

function applyTheme(next: Theme) {
  const root = document.documentElement;
  root.classList.add('theme-switching');
  root.setAttribute('data-theme', next);
  try { localStorage.setItem(THEME_KEY, next); } catch { /* private mode */ }
  window.setTimeout(() => root.classList.remove('theme-switching'), 550);
  listeners.forEach(l => l());
}

export function useTheme(): { theme: Theme; toggle: () => void } {
  const theme = useSyncExternalStore(subscribe, getSnapshot, getServerSnapshot);
  const toggle = useCallback(() => {
    applyTheme(theme === 'dark' ? 'light' : 'dark');
  }, [theme]);
  return { theme, toggle };
}

/* Injected into <head> before paint so there is never a light-mode flash. */
export const THEME_INIT_SCRIPT = `try{var t=localStorage.getItem('${THEME_KEY}');if(t!=='dark'&&t!=='light'){t=window.matchMedia('(prefers-color-scheme: dark)').matches?'dark':'light';}document.documentElement.setAttribute('data-theme',t);}catch(e){}`;
