'use client';

import { Moon, Sun } from 'lucide-react';
import { useTheme } from '@/lib/theme';

export default function ThemeToggle({ className = '' }: { className?: string }) {
  const { theme, toggle } = useTheme();
  const dark = theme === 'dark';

  return (
    <button
      type="button"
      onClick={toggle}
      className={className}
      aria-label={dark ? 'Switch to light mode' : 'Switch to night mode'}
      title={dark ? 'Light mode' : 'Night mode'}
      style={{
        width: 36,
        height: 36,
        borderRadius: '50%',
        border: '1.5px solid var(--color-border)',
        background: 'var(--color-surface)',
        color: dark ? 'var(--color-warning)' : 'var(--color-primary)',
        display: 'inline-flex',
        alignItems: 'center',
        justifyContent: 'center',
        cursor: 'pointer',
        transition: 'transform .25s, border-color .25s, color .45s, background-color .45s',
        flexShrink: 0,
      }}
    >
      <span style={{ display: 'block', animation: 'pageIn .3s ease' }}>
        {dark ? <Sun size={16} /> : <Moon size={16} />}
      </span>
    </button>
  );
}
