'use client';

import styles from './Sunburst.module.css';

const RAY_COUNT = 28;

const CHIPS = [
  { label: 'String 14 · Hotspot', tone: 'red',   top: '8%',  left: '2%'  },
  { label: 'Severity 0.82 · High', tone: 'amber', top: '58%', left: '-4%' },
  { label: 'Fix ETA · 40 min',    tone: 'green', top: '76%', left: '58%' },
];

/**
 * The brand mark, reimagined as a live hero graphic: rays rotate slowly
 * around a pulsing core while small "detection" chips drift in and out,
 * standing in for a real product screenshot without faking one.
 */
export default function Sunburst() {
  return (
    <div className={styles.wrap} aria-hidden="true">
      <div className={styles.ringOuter} />
      <div className={styles.ringInner} />
      <svg className={styles.svg} viewBox="0 0 200 200">
        <g className={styles.rays}>
          {Array.from({ length: RAY_COUNT }).map((_, i) => {
            const angle = (360 / RAY_COUNT) * i;
            const long = i % 2 === 0;
            return (
              <line
                key={i}
                x1="100" y1="100"
                x2="100" y2={long ? '18' : '30'}
                stroke={long ? 'var(--color-accent)' : 'var(--color-primary)'}
                strokeOpacity={long ? 0.9 : 0.35}
                strokeWidth={long ? 4 : 3}
                strokeLinecap="round"
                transform={`rotate(${angle} 100 100)`}
              />
            );
          })}
        </g>
        <circle cx="100" cy="100" r="17" className={styles.core} />
      </svg>

      {CHIPS.map((c, i) => (
        <div
          key={c.label}
          className={`${styles.chip} ${styles['chip_' + c.tone]}`}
          style={{ top: c.top, left: c.left, animationDelay: `${i * 1.4}s` }}
        >
          <span className={styles.chipDot} />
          {c.label}
        </div>
      ))}
    </div>
  );
}
