'use client';

import { useEffect, useState } from 'react';
import styles from './Typewriter.module.css';

const TYPE_MS  = 46;   // per character, with a little human jitter
const ERASE_MS = 24;   // deletion reads faster than typing
const HOLD_MS  = 3000; // linger on a finished line
const BREATH_MS = 520; // beat between one line leaving and the next arriving
const LEAD_MS  = 600;  // a quiet moment before the very first word

/**
 * Types the opening line character by character, lets it sit, then quietly
 * rotates through the remaining lines. Renders its first phrase statically
 * (SSR + reduced motion) and only animates when motion is welcome.
 */
export default function Typewriter({ phrases }: { phrases: string[] }) {
  const [text, setText] = useState(phrases[0] ?? '');

  useEffect(() => {
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;

    let pi = 0;
    let ci = 0;
    let erasing = false;
    let timer: ReturnType<typeof setTimeout>;

    const step = () => {
      const phrase = phrases[pi];
      if (!erasing) {
        ci += 1;
        setText(phrase.slice(0, ci));
        if (ci >= phrase.length) {
          erasing = true;
          timer = setTimeout(step, HOLD_MS);
        } else {
          timer = setTimeout(step, TYPE_MS + Math.random() * 38);
        }
      } else {
        ci -= 1;
        setText(phrase.slice(0, ci));
        if (ci <= 0) {
          erasing = false;
          pi = (pi + 1) % phrases.length;
          timer = setTimeout(step, BREATH_MS);
        } else {
          timer = setTimeout(step, ERASE_MS);
        }
      }
    };

    timer = setTimeout(step, LEAD_MS);
    return () => clearTimeout(timer);
  }, [phrases]);

  return (
    <span className={styles.typed} aria-hidden="true">
      {text}
      <span className={styles.caret} />
    </span>
  );
}
