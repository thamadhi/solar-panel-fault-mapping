'use client';

import styles from './Logo.module.css';

/* ── Wordmark ────────────────────────────────────────────
   "OpenSunray" set as a single styled wordmark: the "Open"
   prefix sits a shade lighter so "Sunray" carries the mark. */
export function LogoWord({ fontSize, className }: { fontSize?: string; className?: string }) {
  return (
    <span className={`${styles.word} ${className ?? ''}`} style={fontSize ? { fontSize } : undefined}>
      <span className={styles.prefix}>Open</span>
      <span className={styles.mark}>Sunray</span>
    </span>
  );
}

export default function Logo({
  fontSize,
  className,
}: {
  fontSize?: string;
  className?: string;
}) {
  return <LogoWord fontSize={fontSize} className={className} />;
}
