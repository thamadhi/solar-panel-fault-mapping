'use client';

import { LayoutGrid, Zap, MapPin, BarChart2, Wrench, History, Settings } from 'lucide-react';
import styles from './ProductPreview.module.css';

const RAIL = [
  { icon: LayoutGrid, label: 'Overview' },
  { icon: Zap,        label: 'Detection', active: true },
  { icon: MapPin,     label: 'Localisation' },
  { icon: BarChart2,  label: 'Severity' },
  { icon: Wrench,     label: 'Rectification' },
  { icon: History,    label: 'History' },
  { icon: Settings,   label: 'Config' },
];

const FAULTS = [
  { string: 'String 03', type: 'Line-Line fault', tone: 'badge-red' },
  { string: 'String 14', type: 'Thermal hotspot',  tone: 'badge-yellow' },
  { string: 'String 22', type: 'Partial shading',  tone: 'badge-blue' },
];

/** A semicircular severity gauge, drawn as two stacked SVG arcs. */
function SeverityGauge({ value = 0.72 }: { value?: number }) {
  const r = 80, cx = 100, cy = 100;
  const circumference = Math.PI * r;
  return (
    <div className={styles.gauge}>
      <svg viewBox="0 0 200 110" width="100%">
        <path
          d={`M ${cx - r} ${cy} A ${r} ${r} 0 0 1 ${cx + r} ${cy}`}
          fill="none" stroke="var(--color-border)" strokeWidth="14" strokeLinecap="round"
        />
        <path
          d={`M ${cx - r} ${cy} A ${r} ${r} 0 0 1 ${cx + r} ${cy}`}
          fill="none" stroke="var(--color-warning)" strokeWidth="14" strokeLinecap="round"
          strokeDasharray={`${circumference * value} ${circumference}`}
        />
      </svg>
      <div className={styles.gaugeLabel}>
        <div className={styles.gaugeValue}>{Math.round(value * 100)}</div>
        <div className={styles.gaugeSub}>Severity score</div>
      </div>
    </div>
  );
}

export default function ProductPreview() {
  return (
    <div className={styles.frame}>
      <div className={styles.chrome}>
        <span className={styles.dot} /><span className={styles.dot} /><span className={styles.dot} />
        <span className={styles.chromeUrl}>opensunray-insight.vercel.app/dashboard</span>
      </div>
      <div className={styles.body}>
        <nav className={styles.rail}>
          {RAIL.map(({ icon: Icon, label, active }) => (
            <div key={label} className={`${styles.railItem} ${active ? styles.active : ''}`}>
              <Icon size={15} /> {label}
            </div>
          ))}
        </nav>
        <div className={styles.main}>
          <div className={styles.mainHead}>
            <h4>Array overview — Block C</h4>
            <span>Updated 4s ago</span>
          </div>
          <div className={styles.split}>
            <SeverityGauge />
            <div className={styles.rows}>
              {FAULTS.map(f => (
                <div key={f.string} className={styles.row}>
                  <span>{f.string}</span>
                  <span className={`badge ${f.tone}`}>{f.type}</span>
                  <span className={styles.rowMuted}>Est. 40 min fix</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
