'use client';

import { useEffect } from 'react';
import { usePathname } from 'next/navigation';
import Lenis from 'lenis';

/**
 * Inertia scrolling for the marketing landing page only.
 *
 * Lenis tracks scroll position internally, separate from the browser's
 * native scrollY, and only reliably recalculates that internal state on
 * window resize. Client-side navigation into the dashboard doesn't resize
 * the window, so Lenis kept the tall landing page's scroll range and target
 * position — the dashboard's shorter, dynamically-loaded content (tables,
 * nested scroll areas, modals) then reads as "scrolling is stuck".
 *
 * Rather than fight that on every route, Lenis is scoped to "/" — the one
 * page it's actually meant to enhance — and fully torn down (Lenis.destroy()
 * removes its classes and listeners) the moment you navigate anywhere else,
 * so the dashboard always gets plain, reliable native scrolling.
 */
export default function SmoothScroll() {
  const pathname = usePathname();
  const enabled = pathname === '/';

  useEffect(() => {
    if (!enabled) return;
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;

    const lenis = new Lenis({
      lerp: 0.09,
      wheelMultiplier: 1,
      anchors: true,
    });

    let raf = 0;
    const loop = (time: number) => {
      lenis.raf(time);
      raf = requestAnimationFrame(loop);
    };
    raf = requestAnimationFrame(loop);

    return () => {
      cancelAnimationFrame(raf);
      lenis.destroy();
    };
  }, [enabled]);

  return null;
}
