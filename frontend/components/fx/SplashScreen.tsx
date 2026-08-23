'use client';

import { useEffect, useState } from 'react';
import Logo from '@/components/ui/Logo';

/**
 * Branded splash shown on first page load, fading out once the app has
 * hydrated (plus a beat so the animation is visible). Unmounts after the fade.
 */
export default function SplashScreen() {
  const [hidden, setHidden] = useState(false);
  const [gone, setGone] = useState(false);

  useEffect(() => {
    const fade = window.setTimeout(() => setHidden(true), 850);
    const remove = window.setTimeout(() => setGone(true), 1500);
    return () => { window.clearTimeout(fade); window.clearTimeout(remove); };
  }, []);

  if (gone) return null;

  return (
    <div className={`splash ${hidden ? 'splashHide' : ''}`} aria-hidden="true">
      <div className="splashLogo">
        <Logo fontSize="clamp(1.15rem, 4vw, 1.6rem)" />
      </div>
      <div className="splashBar" />
      <div className="splashText">Solar Intelligence Hub</div>
    </div>
  );
}
