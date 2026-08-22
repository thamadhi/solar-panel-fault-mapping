'use client';

import { useEffect, useRef } from 'react';

/**
 * Ambient cursor FX: a soft glow orb that trails the pointer (lerped) and a
 * crisp dot that tracks it 1:1. Also powers the card spotlight — while the
 * pointer is over a `.card`, its --mx/--my CSS vars are updated so the radial
 * highlight follows the cursor inside the card.
 *
 * Disabled on touch devices and for reduced-motion users.
 */
export default function CursorGlow() {
  const glowRef = useRef<HTMLDivElement>(null);
  const dotRef  = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (window.matchMedia('(hover: none)').matches) return;
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;

    const glow = glowRef.current;
    const dot  = dotRef.current;
    if (!glow || !dot) return;

    let raf = 0;
    let tx = window.innerWidth / 2;   // pointer x
    let ty = window.innerHeight / 3;  // pointer y
    let gx = tx;                      // lerped glow x
    let gy = ty;

    const onMove = (e: MouseEvent) => {
      tx = e.clientX;
      ty = e.clientY;
      dot.style.transform = `translate(${tx}px, ${ty}px)`;

      const card = (e.target as HTMLElement | null)?.closest?.('.card') as HTMLElement | null;
      if (card) {
        const rect = card.getBoundingClientRect();
        card.style.setProperty('--mx', `${tx - rect.left}px`);
        card.style.setProperty('--my', `${ty - rect.top}px`);
      }
    };

    const loop = () => {
      gx += (tx - gx) * 0.12;
      gy += (ty - gy) * 0.12;
      glow.style.transform = `translate(${gx}px, ${gy}px)`;
      raf = requestAnimationFrame(loop);
    };

    window.addEventListener('mousemove', onMove, { passive: true });
    raf = requestAnimationFrame(loop);

    return () => {
      window.removeEventListener('mousemove', onMove);
      cancelAnimationFrame(raf);
    };
  }, []);

  return (
    <>
      <div ref={glowRef} className="cursor-glow" aria-hidden="true" />
      <div ref={dotRef} className="cursor-dot" aria-hidden="true" />
    </>
  );
}
