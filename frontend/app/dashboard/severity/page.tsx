'use client';

import { useRef, useState } from 'react';
import { predictElectrical, predictImage, explainElectrical } from '@/lib/api';
import { logPrediction } from '@/lib/predictions-log';
import { useAuth } from '@/lib/AuthContext';
import { ROLE_PERMISSIONS } from '@/components/layout/DashboardLayout';
import { Gauge, Zap, Image as ImageIcon, ShieldAlert, Info } from 'lucide-react';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, Cell,
} from 'recharts';
import styles from './page.module.css';

type Tab = 'csv' | 'image';

interface ExplainRow {
  feature: string;
  value: number;
  impact: number;
  direction: string;
}

const COLUMN_ALIASES: Record<string, string> = { irr: 'irradiance', pvt: 'temperature' };
const REQUIRED = ['vdc1', 'vdc2', 'idc1', 'idc2', 'irradiance', 'temperature'];

function bandFor(score: number): { label: string; cls: string } {
  if (score <= 0.3) return { label: 'Low',      cls: styles.low };
  if (score <= 0.6) return { label: 'Medium',   cls: styles.medium };
  if (score <= 0.8) return { label: 'High',     cls: styles.high };
  return                  { label: 'Critical',  cls: styles.critical };
}

export default function SeverityPage() {
  const { user } = useAuth();
  const allowed = (ROLE_PERMISSIONS[user?.type ?? 'Standard'] ?? []).includes('Severity');

  const [tab, setTab]               = useState<Tab>('csv');
  const [csvFile, setCsvFile]       = useState<File | null>(null);
  const [imgFile, setImgFile]       = useState<File | null>(null);
  const [imgPreview, setImgPreview] = useState<string | null>(null);
  const [riskScore, setRiskScore]   = useState<number | null>(null);
  const [band, setBand]             = useState<{ label: string; cls: string } | null>(null);
  const [predLabel, setPredLabel]   = useState<string | null>(null);
  const [confidence, setConfidence] = useState<number | null>(null);
  const [contributors, setContributors] = useState<ExplainRow[] | null>(null);
  const [loading, setLoading]       = useState(false);
  const [error, setError]           = useState('');
  const fileRef = useRef<HTMLInputElement>(null);
  const imgRef  = useRef<HTMLInputElement>(null);

  async function handleElectrical() {
    if (!csvFile) return;
    setLoading(true); setError(''); setRiskScore(null); setContributors(null); setPredLabel(null);
    try {
      // Parse CSV and normalise column aliases
      const lines = (await csvFile.text()).trim().split('\n');
      let headers = lines[0].split(',').map(h => h.trim());
      headers = headers.map(h => COLUMN_ALIASES[h.toLowerCase()] ?? h.toLowerCase());
      const missing = REQUIRED.filter(c => !headers.includes(c));
      if (missing.length) throw new Error(`Missing columns: ${missing.join(', ')}`);

      const records = lines.slice(1).map(line => {
        const vals = line.split(',');
        const obj: Record<string, number> = {};
        headers.forEach((h, i) => { obj[h] = parseFloat(vals[i]?.trim() ?? '0'); });
        return obj;
      });

      const pred  = await predictElectrical(records);
      const label = String(pred.fault_type);
      const conf  = Number(pred.confidence ?? 0);
      setPredLabel(label);
      setConfidence(conf);

      // SHAP contributions for the first row drive the derived risk index
      const exp = await explainElectrical(records, 0);
      const rows: ExplainRow[] = exp.contributors ?? [];
      setContributors(rows);

      const isNormal = /normal|healthy/i.test(label);
      const meanAbsShap = rows.length
        ? rows.reduce((s, r) => s + Math.abs(r.impact), 0) / rows.length
        : 0.5;
      // Heuristic blend of model confidence and SHAP magnitude — NOT the
      // production XGBoost severity model (not exposed by the API).
      const score = isNormal ? Math.min(0.3, conf * 0.2) : Math.min(1, 0.35 * (1 - conf) + 0.65 * meanAbsShap);
      const b = bandFor(score);
      setRiskScore(score); setBand(b);

      logPrediction({ source: 'Fault Severity', mode: 'electrical', fault_type: label, confidence: conf });
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Severity analysis failed');
    } finally { setLoading(false); }
  }

  function handleImageSelect(file: File) {
    setImgFile(file);
    setImgPreview(URL.createObjectURL(file));
  }

  async function handleImage() {
    if (!imgFile) return;
    setLoading(true); setError(''); setRiskScore(null); setContributors(null); setPredLabel(null);
    try {
      const pred = await predictImage(imgFile);
      const label = String(pred.fault_type);
      const conf = Number(pred.confidence ?? 0);
      setPredLabel(label); setConfidence(conf);
      const b = bandFor(/normal|healthy|no fault/i.test(label) ? 0.15 : Math.min(1, 1 - conf));
      setBand(b); setRiskScore(/normal|healthy|no fault/i.test(label) ? 0.15 : Math.min(1, 1 - conf));
      logPrediction({ source: 'Fault Severity', mode: 'thermal', fault_type: label, confidence: conf });
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Image severity analysis failed');
    } finally { setLoading(false); }
  }

  if (!allowed) {
    return (
      <div>
        <div className="page-title">🛡️ Fault Severity Analysis</div>
        <div className="page-sub">XGBOOST RISK SCORING</div>
        <div className="card">
          <div className="alert alert-warning"><ShieldAlert size={16} /> Your role ({user?.type}) does not include access to severity analysis.</div>
        </div>
      </div>
    );
  }

  return (
    <div>
      <div className="page-title">🛡️ Fault Severity Analysis</div>
      <div className="page-sub">ELECTRICAL · THERMAL SCORING</div>

      <div className="tabs-nav" style={{ marginBottom: '1.5rem' }}>
        <button className={`tab-btn ${tab === 'csv' ? 'active' : ''}`} onClick={() => { setTab('csv'); setError(''); }}>⚡ Electrical Analysis</button>
        <button className={`tab-btn ${tab === 'image' ? 'active' : ''}`} onClick={() => { setTab('image'); setError(''); }}>🖼️ Image Model Analysis</button>
      </div>

      {tab === 'csv' && (
        <>
          <div className="card" style={{ marginBottom: '1rem' }}>
            <div className="alert alert-info" style={{ marginBottom: '1rem' }}>
              <Info size={14} /> Required columns: <code>vdc1, vdc2, idc1, idc2, irradiance</code> (or <code>irr</code>), <code>temperature</code> (or <code>pvt</code>)
            </div>
            <div className={`upload-zone ${csvFile ? styles.uploadActive : ''}`} onClick={() => fileRef.current?.click()}>
              <input ref={fileRef} type="file" accept=".csv" onChange={e => { if (e.target.files?.[0]) setCsvFile(e.target.files[0]); }} />
              <div className="upload-icon"><Zap size={36} color="var(--color-muted)" /></div>
              {csvFile ? (
                <div className="upload-label" style={{ color: 'var(--color-accent)', fontWeight: 600 }}>✓ {csvFile.name}</div>
              ) : (
                <>
                  <div className="upload-label">Click to upload sensor CSV</div>
                  <div className="upload-hint">Supported: .csv</div>
                </>
              )}
            </div>
            <button className="btn btn-primary btn-full" style={{ marginTop: '1rem' }} disabled={!csvFile || loading} onClick={handleElectrical}>
              {loading ? <><span className="spinner" style={{ width:16, height:16, borderWidth:2 }} /> Scoring…</> : <><Gauge size={16} /> Run Sensor AI</>}
            </button>
          </div>

          {error && <div className="alert alert-error">{error}</div>}

          {band && riskScore != null && (
            <>
              <div className="grid-3" style={{ marginBottom: '1rem' }}>
                <div className={`metric-card ${styles.scoreCard} ${band.cls}`}>
                  <div className="metric-label">Derived Risk Index</div>
                  <div className="metric-value">{riskScore.toFixed(2)}</div>
                </div>
                <div className={`metric-card ${styles.scoreCard} ${band.cls}`}>
                  <div className="metric-label">Level</div>
                  <div className="metric-value">{band.label}</div>
                </div>
                <div className="metric-card blue">
                  <div className="metric-label">Classification · Confidence</div>
                  <div className="metric-value" style={{ fontSize: '1.3rem' }}>{predLabel}{confidence != null ? ` · ${(confidence * 100).toFixed(1)}%` : ''}</div>
                </div>
              </div>

              <div className="alert alert-warning" style={{ marginBottom: '1rem' }}>
                Risk index is a heuristic derived from model confidence + SHAP magnitudes — the dedicated XGBoost severity model is not exposed by the API.
              </div>

              {contributors && contributors.length > 0 && (
                <div className="card">
                  <div className="section-label">SHAP Feature Contributions — first row</div>
                  <ResponsiveContainer width="100%" height={Math.max(220, contributors.length * 38)}>
                    <BarChart data={contributors} layout="vertical" margin={{ left: 30, right: 20 }}>
                      <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" />
                      <XAxis type="number" tick={{ fontSize: 11 }} />
                      <YAxis type="category" dataKey="feature" width={110} tick={{ fontSize: 11 }} />
                      <Tooltip />
                      <Bar dataKey="impact" radius={[0, 4, 4, 0]}>
                        {contributors.map((r, i) => (
                          <Cell key={i} fill={r.impact >= 0 ? '#ef4444' : '#00cc96'} />
                        ))}
                      </Bar>
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              )}
            </>
          )}
        </>
      )}

      {tab === 'image' && (
        <>
          <div className="card" style={{ marginBottom: '1rem' }}>
            <div className={`upload-zone ${imgFile ? styles.uploadActive : ''}`} onClick={() => imgRef.current?.click()}>
              <input ref={imgRef} type="file" accept="image/*" onChange={e => { if (e.target.files?.[0]) handleImageSelect(e.target.files[0]); }} />
              <div className="upload-icon"><ImageIcon size={36} color="var(--color-muted)" /></div>
              {imgFile ? (
                <div className="upload-label" style={{ color: 'var(--color-accent)', fontWeight: 600 }}>✓ {imgFile.name}</div>
              ) : (
                <>
                  <div className="upload-label">Click to upload thermal image</div>
                  <div className="upload-hint">Supported: .jpg, .jpeg, .png</div>
                </>
              )}
            </div>
            {imgPreview && (
              <div className={styles.imgPreview}>
                {/* eslint-disable-next-line @next/next/no-img-element */}
                <img src={imgPreview} alt="Preview" />
              </div>
            )}
            <button className="btn btn-primary btn-full" style={{ marginTop: '1rem' }} disabled={!imgFile || loading} onClick={handleImage}>
              {loading ? <><span className="spinner" style={{ width:16, height:16, borderWidth:2 }} /> Processing…</> : <><Gauge size={16} /> Run Image AI</>}
            </button>
          </div>

          {error && <div className="alert alert-error">{error}</div>}

          {band && riskScore != null && predLabel && (
            <div className="card">
              <div className="grid-3">
                <div className={`metric-card ${styles.scoreCard} ${band.cls}`}>
                  <div className="metric-label">Derived Risk Index</div>
                  <div className="metric-value">{riskScore.toFixed(2)}</div>
                </div>
                <div className={`metric-card ${styles.scoreCard} ${band.cls}`}>
                  <div className="metric-label">Classification</div>
                  <div className="metric-value" style={{ fontSize: '1.3rem' }}>{predLabel}</div>
                </div>
                <div className="metric-card blue">
                  <div className="metric-label">Model Confidence</div>
                  <div className="metric-value">{confidence != null ? `${(confidence * 100).toFixed(1)}%` : '—'}</div>
                </div>
              </div>
              <div className="alert alert-warning" style={{ marginTop: '1rem' }}>
                Hotspot counts / panel ratio come from the vision severity pipeline which is not exposed by the API; classification confidence is used as the impact proxy.
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
}
