'use client';

import { useEffect, useId, useRef } from 'react';
import styles from './Logo.module.css';

/* ── Dynamic eye ─────────────────────────────────────────
   The dot of the “i” is an eye whose gaze drifts downward
   as the page scrolls, with a periodic blink. */
export function LogoWord({ fontSize, className }: { fontSize?: string; className?: string }) {
  const uid = useId();
  const irisRef = useRef<SVGGElement | null>(null);
  const clipId = `pv-eye-clip-${uid}`;
  const irisGradId = `pv-iris-${uid}`;

  useEffect(() => {
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
    let raf = 0;
    const update = () => {
      raf = 0;
      const doc = document.documentElement;
      const max = Math.max(doc.scrollHeight - window.innerHeight, 1);
      const p = Math.min(Math.max(window.scrollY / max, 0), 1);
      if (irisRef.current) {
        irisRef.current.style.transform = `translateY(${(p * 4.4).toFixed(2)}px)`;
      }
    };
    const onScroll = () => { if (!raf) raf = requestAnimationFrame(update); };
    update();
    window.addEventListener('scroll', onScroll, { passive: true });
    window.addEventListener('resize', onScroll);
    return () => {
      window.removeEventListener('scroll', onScroll);
      window.removeEventListener('resize', onScroll);
      if (raf) cancelAnimationFrame(raf);
    };
  }, []);

  return (
    <span className={`${styles.word} ${className ?? ''}`} style={fontSize ? { fontSize } : undefined}>
      OpenPV
      <span className={styles.iStem}>
        {'\u0131'}
        <svg
          className={styles.eye}
          viewBox="0 0 34 20"
          aria-hidden="true"
          focusable="false"
        >
          <defs>
            <clipPath id={clipId}>
              <path d="M1.2 10 C7 2.6 27 2.6 32.8 10 C27 17.4 7 17.4 1.2 10 Z" />
            </clipPath>
            <radialGradient id={irisGradId} cx="42%" cy="38%" r="72%">
              <stop offset="0%" stopColor="#9ecbff" />
              <stop offset="55%" stopColor="#3b82f6" />
              <stop offset="100%" stopColor="#1d4ed8" />
            </radialGradient>
          </defs>
          <g className={styles.blink}>
            <path
              d="M1.2 10 C7 2.6 27 2.6 32.8 10 C27 17.4 7 17.4 1.2 10 Z"
              fill="var(--color-surface)"
            />
            <g ref={irisRef} clipPath={`url(#${clipId})`} className={styles.iris}>
              <circle cx="17" cy="10" r="5" fill={`url(#${irisGradId})`} />
              <circle cx="17" cy="10" r="2.2" fill="#0d2242" />
              <circle cx="19.2" cy="7.6" r="1" fill="#ffffff" opacity="0.85" />
            </g>
            <path
              d="M1.2 10 C7 2.6 27 2.6 32.8 10 C27 17.4 7 17.4 1.2 10 Z"
              fill="none"
              stroke="currentColor"
              strokeWidth="2.4"
              strokeLinejoin="round"
            />
          </g>
        </svg>
      </span>
      sor
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
