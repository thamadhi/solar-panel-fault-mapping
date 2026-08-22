'use client';

import { useState } from 'react';
import { HelpCircle, ChevronDown } from 'lucide-react';

const FAQS = [
  {
    q: 'What columns does my electrical CSV need?',
    a: 'Fault Detection and Localisation expect vdc1, vdc2, idc1, idc2, irradiance, temperature. Severity also accepts the aliases irr (irradiance) and pvt (temperature). Values must be numeric with no empty cells.',
  },
  {
    q: 'How is confidence interpreted?',
    a: 'Confidence is the model probability (0–100%) for the predicted class. High confidence on a fault class means strong evidence of a real fault; high confidence on "Normal" means readings look healthy.',
  },
  {
    q: 'What do the different roles allow?',
    a: 'Technician: detection, localisation, rectification, history, config. Solar PV Operator adds severity. Admin has all pages. Standard accounts see the dashboard only. The sidebar hides pages your role cannot access.',
  },
  {
    q: 'What kind of thermal images work best?',
    a: 'Use EL/IR panel photos where hotspots are visible — JPEG or PNG. Very dark, blurred or distant array shots reduce model confidence.',
  },
  {
    q: 'How are rectification costs calculated?',
    a: 'The recommendation engine scores candidate actions (cleaning, rewiring, replacement…) against fault type, severity and weather, then ranks them by expected cost and downtime. The Best Action card shows the top-ranked choice.',
  },
  {
    q: 'Where is my prediction history stored?',
    a: 'Activity is recorded per browser as you run predictions (the API does not expose a history endpoint). Use Export CSV on the Activity Log page to keep an archive, and Clear Log to reset it.',
  },
];

const COLUMNS = [
  ['vdc1', 'String 1 DC voltage (V)'],
  ['vdc2', 'String 2 DC voltage (V)'],
  ['idc1', 'String 1 DC current (A)'],
  ['idc2', 'String 2 DC current (A)'],
  ['irradiance', 'Plane-of-array irradiance (W/m²)'],
  ['temperature', 'Panel / ambient temperature (°C)'],
];

const GUIDES = [
  ['Run a batch electrical analysis', 'Dashboard → Fault Detection → CSV Batch Analysis → upload CSV → Analyze. Click Explain on any row for SHAP feature contributions.'],
  ['Localise a hotspot', 'Dashboard → Localisation → Thermal Image → upload → Locate Hotspot Region. The annotated overlay highlights the faulty region with its bounding box.'],
  ['Get a repair plan', 'Dashboard → Rectification → fill in fault type, severity, weather and site details → Get Recommendations. Compare cost/downtime, then follow the Best Action card.'],
];

export default function HelpPage() {
  const [openIdx, setOpenIdx] = useState<number | null>(0);

  return (
    <div>
      <div className="page-title">❓ Support Center</div>
      <div className="page-sub">FAQ · REFERENCE · GUIDES</div>

      <div className="section-label">Frequently Asked Questions</div>
      {FAQS.map((f, i) => (
        <div key={i} className="accordion-item">
          <div className="accordion-header" onClick={() => setOpenIdx(openIdx === i ? null : i)}>
            <span style={{ display: 'inline-flex', alignItems: 'center', gap: '0.5rem' }}><HelpCircle size={15} color="var(--color-accent)" /> {f.q}</span>
            <ChevronDown size={16} style={{ transform: openIdx === i ? 'rotate(180deg)' : 'none', transition: 'transform .2s' }} />
          </div>
          {openIdx === i && <div className="accordion-body">{f.a}</div>}
        </div>
      ))}

      <div className="section-label">CSV Column Reference</div>
      <div className="card" style={{ marginBottom: '1.5rem' }}>
        <div style={{ overflowX: 'auto' }}>
          <table className="data-table">
            <thead><tr><th>Column</th><th>Description</th></tr></thead>
            <tbody>
              {COLUMNS.map(([col, desc]) => (
                <tr key={col}><td><code>{col}</code></td><td>{desc}</td></tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      <div className="section-label">Step-by-Step Guides</div>
      {GUIDES.map(([title, body], i) => (
        <div key={i} className="card" style={{ marginBottom: '0.75rem' }}>
          <h3 style={{ marginBottom: '0.4rem' }}>{i + 1}. {title}</h3>
          <p style={{ fontSize: '0.85rem', color: 'var(--color-muted)' }}>{body}</p>
        </div>
      ))}
    </div>
  );
}
