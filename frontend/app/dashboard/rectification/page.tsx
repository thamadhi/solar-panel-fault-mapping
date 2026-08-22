'use client';

import { useState } from 'react';
import { rectifyFault } from '@/lib/api';
import { logPrediction } from '@/lib/predictions-log';
import { Wrench, Zap, BadgeDollarSign, Clock, Star } from 'lucide-react';
import styles from './page.module.css';

const FAULT_TYPES = ['Open Circuit', 'Short Circuit', 'Hotspot', 'Shadowing'];
const SEVERITIES  = ['Low', 'Medium', 'High', 'Critical'];
const WEATHER     = ['Sunny', 'Cloudy', 'Rainy'];

interface RectifyResult {
  status: string;
  fault_type: string;
  location: string;
  severity: string;
  confidence: number;
  recommendations: { action: string; confidence: number; cost: number; downtime: number }[];
  best_action: string;
  best_cost: number;
  best_downtime: number;
}

export default function RectificationPage() {
  const [form, setForm] = useState({
    fault_type: '', severity_level: '', weather_condition: '',
    string_num: '', panel_num: '', irradiance: '', module_age_years: '',
  });
  const [result, setResult]   = useState<RectifyResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError]     = useState('');

  function set<K extends keyof typeof form>(key: K, value: string) {
    setForm(prev => ({ ...prev, [key]: value }));
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(''); setResult(null);
    if (Object.values(form).some(v => !v)) {
      setError('Please fill in all fields before predicting.');
      return;
    }
    setLoading(true);
    try {
      const payload = {
        fault_type:        form.fault_type,
        severity_level:    form.severity_level,
        weather_condition: form.weather_condition,
        string_num:        parseInt(form.string_num, 10),
        panel_num:         parseInt(form.panel_num, 10),
        irradiance:        parseFloat(form.irradiance),
        module_age_years:  parseInt(form.module_age_years, 10),
      };
      const data = (await rectifyFault(payload)) as unknown as RectifyResult;
      setResult(data);
      logPrediction({
        source: 'Rectification',
        mode: 'rectification',
        fault_type: String(data.fault_type),
        confidence: Number(data.confidence ?? 0) > 1 ? Number(data.confidence) / 100 : Number(data.confidence ?? 0),
      });
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Rectification failed');
    } finally { setLoading(false); }
  }

  return (
    <div>
      <div className="page-title">🔧 Fault Rectification</div>
      <div className="page-sub">RECOMMENDATION ENGINE · COST &amp; DOWNTIME</div>

      <form onSubmit={handleSubmit}>
        <div className="card" style={{ marginBottom: '1rem' }}>
          <div className="grid-3">
            <div className="form-group">
              <label className="form-label">Fault Type</label>
              <select className="form-select" value={form.fault_type} onChange={e => set('fault_type', e.target.value)} required>
                <option value="" disabled>Select fault type</option>
                {FAULT_TYPES.map(f => <option key={f} value={f}>{f}</option>)}
              </select>
            </div>
            <div className="form-group">
              <label className="form-label">Severity</label>
              <select className="form-select" value={form.severity_level} onChange={e => set('severity_level', e.target.value)} required>
                <option value="" disabled>Select severity</option>
                {SEVERITIES.map(s => <option key={s} value={s}>{s}</option>)}
              </select>
            </div>
            <div className="form-group">
              <label className="form-label">Weather</label>
              <select className="form-select" value={form.weather_condition} onChange={e => set('weather_condition', e.target.value)} required>
                <option value="" disabled>Select weather</option>
                {WEATHER.map(w => <option key={w} value={w}>{w}</option>)}
              </select>
            </div>
          </div>

          <div className="grid-4">
            <div className="form-group">
              <label className="form-label">String #</label>
              <input className="form-input" type="number" min="1" placeholder="e.g. 12" value={form.string_num} onChange={e => set('string_num', e.target.value)} required />
            </div>
            <div className="form-group">
              <label className="form-label">Panel #</label>
              <input className="form-input" type="number" min="1" placeholder="e.g. 7" value={form.panel_num} onChange={e => set('panel_num', e.target.value)} required />
            </div>
            <div className="form-group">
              <label className="form-label">Irradiance (W/m²)</label>
              <input className="form-input" type="number" step="any" min="0" placeholder="e.g. 850" value={form.irradiance} onChange={e => set('irradiance', e.target.value)} required />
            </div>
            <div className="form-group">
              <label className="form-label">Module Age (years)</label>
              <input className="form-input" type="number" min="0" placeholder="e.g. 5" value={form.module_age_years} onChange={e => set('module_age_years', e.target.value)} required />
            </div>
          </div>

          {error && <div className="alert alert-error" style={{ marginBottom: '1rem' }}>{error}</div>}

          <button type="submit" className="btn btn-primary btn-full" disabled={loading}>
            {loading ? <><span className="spinner" style={{ width:16, height:16, borderWidth:2 }} /> Predicting…</> : <><Zap size={16} /> Get Recommendations</>}
          </button>
        </div>
      </form>

      {result && (
        <>
          {/* Fault overview */}
          <div className="section-label">Fault Overview</div>
          <div className="grid-4" style={{ marginBottom: '1.25rem' }}>
            <div className="metric-card"><div className="metric-label">Fault Type</div><div className="metric-value" style={{ fontSize: '1.15rem' }}>{result.fault_type}</div></div>
            <div className="metric-card"><div className="metric-label">Location</div><div className="metric-value" style={{ fontSize: '1.15rem' }}>{result.location || '—'}</div></div>
            <div className={`metric-card ${/low/i.test(result.severity) ? '' : /critical/i.test(result.severity) ? 'red' : 'yellow'}`}>
              <div className="metric-label">Severity</div><div className="metric-value" style={{ fontSize: '1.15rem' }}>{result.severity}</div>
            </div>
            <div className="metric-card blue">
              <div className="metric-label">Confidence</div>
              <div className="metric-value">{typeof result.confidence === 'number' ? (result.confidence > 1 ? result.confidence.toFixed(0) : (result.confidence * 100).toFixed(1)) : '—'}%</div>
            </div>
          </div>

          {/* Recommended actions */}
          <div className="section-label">Recommended Actions</div>
          <div className="grid-3" style={{ marginBottom: '1.25rem' }}>
            {result.recommendations?.map((r, i) => (
              <div key={i} className="card">
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.75rem' }}>
                  <span className="badge badge-green">Action {i + 1}</span>
                  {r.confidence >= Math.max(...result.recommendations.map(x => x.confidence)) && (
                    <span className="badge badge-blue"><Star size={10} /> Top match</span>
                  )}
                </div>
                <p style={{ fontWeight: 600, fontSize: '0.88rem', marginBottom: '0.6rem' }}>{r.action}</p>
                <div className={styles.actionMeta}>
                  <span><Wrench size={12} /> Confidence {typeof r.confidence === 'number' ? r.confidence.toFixed(0) : r.confidence}%</span>
                  <span><BadgeDollarSign size={12} /> ${r.cost}</span>
                  <span><Clock size={12} /> {r.downtime} hrs</span>
                </div>
              </div>
            ))}
          </div>

          {/* Best action */}
          <div className={styles.bestCard}>
            <div className={styles.bestLabel}>★ Best Action</div>
            <div className={styles.bestAction}>{result.best_action}</div>
            <div className={styles.bestMeta}>
              Cost: <strong>${result.best_cost}</strong> &nbsp;·&nbsp; Downtime: <strong>{result.best_downtime} hrs</strong>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
