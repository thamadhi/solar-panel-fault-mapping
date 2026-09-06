'use client';

import { useEffect, useRef } from 'react';
import styles from './BotAvatar.module.css';

/**
 * A small bot face used on the chat launcher: its eyes drift toward the
 * cursor wherever it goes on the page, and it blinks on its own, so the
 * "ask a question" affordance feels alive instead of a static icon. Purely
 * cosmetic (aria-hidden) — the button it sits in carries the real label.
 * Falls back to a still face when the visitor prefers reduced motion.
 */
export default function BotAvatar({ size = 26 }: { size?: number }) {
  const wrapRef = useRef<HTMLDivElement>(null);
  const eyesRef = useRef<SVGGElement>(null);
  const lidsRef = useRef<SVGGElement>(null);

  useEffect(() => {
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;

    const MAX_SHIFT = 2.6;
    let raf = 0;
    let targetX = 0, targetY = 0;
    let curX = 0, curY = 0;

    const onMove = (e: MouseEvent) => {
      const el = wrapRef.current;
      if (!el) return;
      const rect = el.getBoundingClientRect();
      const dx = e.clientX - (rect.left + rect.width / 2);
      const dy = e.clientY - (rect.top + rect.height / 2);
      const dist = Math.hypot(dx, dy) || 1;
      const shift = Math.min(MAX_SHIFT, dist / 40);
      targetX = (dx / dist) * shift;
      targetY = (dy / dist) * shift;
    };

    const loop = () => {
      curX += (targetX - curX) * 0.25;
      curY += (targetY - curY) * 0.25;
      if (eyesRef.current) eyesRef.current.style.transform = `translate(${curX}px, ${curY}px)`;
      raf = requestAnimationFrame(loop);
    };

    window.addEventListener('mousemove', onMove, { passive: true });
    raf = requestAnimationFrame(loop);

    let blinkTimer: ReturnType<typeof setTimeout>;
    let hideTimer: ReturnType<typeof setTimeout>;
    const scheduleBlink = () => {
      blinkTimer = setTimeout(() => {
        lidsRef.current?.classList.add(styles.blinking);
        hideTimer = setTimeout(() => lidsRef.current?.classList.remove(styles.blinking), 140);
        scheduleBlink();
      }, 2600 + Math.random() * 3000);
    };
    scheduleBlink();

    return () => {
      window.removeEventListener('mousemove', onMove);
      cancelAnimationFrame(raf);
      clearTimeout(blinkTimer);
      clearTimeout(hideTimer);
    };
  }, []);

  return (
    <div ref={wrapRef} className={styles.wrap} style={{ width: size, height: size }} aria-hidden="true">
      <svg viewBox="0 0 40 40" width={size} height={size}>
        <line x1="20" y1="4" x2="20" y2="9" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
        <circle cx="20" cy="3" r="2" fill="currentColor" />
        <rect x="6" y="9" width="28" height="24" rx="10" fill="currentColor" />
        <g ref={eyesRef}>
          <g ref={lidsRef} className={styles.eyes}>
            <circle className={styles.eye} cx="16" cy="21" r="3.1" />
            <circle className={styles.eye} cx="24" cy="21" r="3.1" />
          </g>
        </g>
      </svg>
    </div>
  );
}
