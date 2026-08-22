'use client';

import { useState, useRef } from 'react';
import { predictElectrical, predictImage, explainElectrical } from '@/lib/api';
import { Upload, Zap, Image as ImageIcon } from 'lucide-react';
import styles from './page.module.css';

type Tab = 'csv' | 'image';

interface FaultResult {
  fault_type: string;
  confidence: number;
  result_readings?: Record<string, number>[];
}

interface ExplainRow {
  feature: string;
  value: number;
  impact: number;
  direction: string;
}

export default function DetectionPage() {
  const [tab, setTab]               = useState<Tab>('csv');
  const [csvFile, setCsvFile]       = useState<File | null>(null);
  const [imgFile, setImgFile]       = useState<File | null>(null);
  const [imgPreview, setImgPreview] = useState<string | null>(null);
  const [result, setResult]         = useState<FaultResult | null>(null);
  const [explain, setExplain]       = useState<ExplainRow[] | null>(null);
  const [selectedRow, setSelectedRow] = useState<number | null>(null);
  const [loading, setLoading]       = useState(false);
  const [explainLoading, setExplainLoading] = useState(false);
  const [error, setError]           = useState('');
  const [records, setRecords]       = useState<Record<string, number>[]>([]);
  const fileRef  = useRef<HTMLInputElement>(null);
  const imgRef   = useRef<HTMLInputElement>(null);

  /* ── CSV mode ── */
  async function handleCSVAnalyze() {
    if (!csvFile) return;
    setLoading(true); setError(''); setResult(null); setExplain(null);
    try {
      const text = await csvFile.text();
      const lines = text.trim().split('\n');
      const headers = lines[0].split(',').map(h => h.trim());
      const parsed: Record<string, number>[] = lines.slice(1).map(line => {
        const vals = line.split(',');
        const obj: Record<string, number> = {};
        headers.forEach((h, i) => { obj[h] = parseFloat(vals[i]?.trim() ?? '0'); });
        return obj;
      });
      setRecords(parsed);
      const data = await predictElectrical(parsed);
      setResult(data);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Prediction failed');
    } finally { setLoading(false); }
  }

  async function handleExplain(rowIdx: number) {
    if (!records.length) return;
    setExplainLoading(true); setExplain(null); setSelectedRow(rowIdx);
    try {
      const data = await explainElectrical(records, rowIdx);
      setExplain(data.contributors || []);
    } catch { setExplain([]); }
    finally { setExplainLoading(false); }
  }

  /* ── Image mode ── */
  function handleImageSelect(file: File) {
    setImgFile(file);
    const url = URL.createObjectURL(file);
    setImgPreview(url);
    setResult(null); setError('');
  }

  async function handleImageScan() {
    if (!imgFile) return;
    setLoading(true); setError(''); setResult(null);
    try {
      const data = await predictImage(imgFile);
      setResult(data);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Image scan failed');
    } finally { setLoading(false); }
  }

  const confidencePct = result ? (result.confidence * 100).toFixed(1) : null;
  const isNormal      = result?.fault_type === 'Normal' || result?.fault_type === 'Healthy';

  return (
    <div>
      <div className="page-title">⚡ Fault Detection</div>
      <div className="page-sub">ELECTRICAL · THERMAL ANALYSIS</div>

      <div className="tabs-nav" style={{ marginBottom: '1.5rem' }}>
        <button className={`tab-btn ${tab === 'csv' ? 'active' : ''}`} onClick={() => { setTab('csv'); setResult(null); setError(''); }}>
          📄 CSV Batch Analysis
        </button>
        <button className={`tab-btn ${tab === 'image' ? 'active' : ''}`} onClick={() => { setTab('image'); setResult(null); setError(''); }}>
          🖼️ Thermal Vision
        </button>
      </div>

      {/* CSV Tab */}
      {tab === 'csv' && (
        <div className={styles.tabContent}>
          <div className="card" style={{ marginBottom: '1rem' }}>
            <div className="alert alert-info" style={{ marginBottom: '1rem' }}>
              Your CSV must contain: <code>vdc1</code>, <code>vdc2</code>, <code>idc1</code>, <code>idc2</code>, <code>irradiance</code>, <code>temperature</code>
            </div>
            <div
              className={`upload-zone ${csvFile ? styles.uploadActive : ''}`}
              onClick={() => fileRef.current?.click()}
            >
              <input ref={fileRef} type="file" accept=".csv" onChange={e => { if (e.target.files?.[0]) setCsvFile(e.target.files[0]); }} />
              <div className="upload-icon"><Upload size={36} color="var(--color-muted)" /></div>
              {csvFile ? (
                <div className="upload-label" style={{ color: 'var(--color-accent)', fontWeight: 600 }}>✓ {csvFile.name}</div>
              ) : (
                <>
                  <div className="upload-label">Click to upload CSV file</div>
                  <div className="upload-hint">Supported: .csv</div>
                </>
              )}
            </div>
            <button
              className="btn btn-primary btn-full"
              style={{ marginTop: '1rem' }}
              disabled={!csvFile || loading}
              onClick={handleCSVAnalyze}
            >
              {loading ? <><span className="spinner" style={{width:16,height:16,borderWidth:2}} /> Analyzing…</> : <><Zap size={16} /> Analyze CSV Data</>}
            </button>
          </div>

          {error && <div className="alert alert-error">{error}</div>}

          {result && (
            <div className="card">
              <div className={styles.resultHeader}>
                <span className={`badge ${isNormal ? 'badge-green' : 'badge-red'}`} style={{ fontSize: '1rem', padding: '6px 18px' }}>
                  {result.fault_type}
                </span>
                <span style={{ color: 'var(--color-muted)', fontSize: '0.82rem' }}>
                  Confidence: <strong>{confidencePct}%</strong>
                </span>
              </div>

              {result.result_readings && result.result_readings.length > 0 && (
                <>
                  <div className="section-label">Prediction Results — Click a row to explain</div>
                  <div style={{ overflowX: 'auto' }}>
                    <table className="data-table">
                      <thead>
                        <tr>
                          <th>#</th>
                          {Object.keys(result.result_readings[0]).map(k => <th key={k}>{k}</th>)}
                          <th>Explain</th>
                        </tr>
                      </thead>
                      <tbody>
                        {result.result_readings.slice(0, 20).map((row, i) => (
                          <tr key={i} className={selectedRow === i ? 'selected' : ''}>
                            <td>{i + 1}</td>
                            {Object.values(row).map((v, j) => <td key={j}>{typeof v === 'number' ? v.toFixed(3) : String(v)}</td>)}
                            <td>
                              <button className="btn btn-outline btn-sm" onClick={() => handleExplain(i)}>
                                {selectedRow === i && explainLoading ? <span className="spinner" style={{width:12,height:12,borderWidth:2}} /> : 'Explain'}
                              </button>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </>
              )}

              {explain !== null && (
                <div style={{ marginTop: '1.5rem' }}>
                  <div className="section-label">AI Explanation — Row {(selectedRow ?? 0) + 1}</div>
                  {explain.length === 0 ? (
                    <div className="alert alert-warning">No explanation available.</div>
                  ) : (
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                      {explain.map(row => (
                        <div key={row.feature} className={styles.explainRow}>
                          <span className={styles.explainFeature}>{row.feature}</span>
                          <span className={styles.explainValue}>= {row.value.toFixed(3)}</span>
                          <span className={`badge ${row.impact >= 0 ? 'badge-red' : 'badge-green'}`}>
                            {row.direction} ({row.impact >= 0 ? '+' : ''}{row.impact.toFixed(3)})
                          </span>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* Image Tab */}
      {tab === 'image' && (
        <div className={styles.tabContent}>
          <div className="card" style={{ marginBottom: '1rem' }}>
            <div
              className={`upload-zone ${imgFile ? styles.uploadActive : ''}`}
              onClick={() => imgRef.current?.click()}
            >
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

            <button
              className="btn btn-primary btn-full"
              style={{ marginTop: '1rem' }}
              disabled={!imgFile || loading}
              onClick={handleImageScan}
            >
              {loading ? <><span className="spinner" style={{width:16,height:16,borderWidth:2}} /> Scanning…</> : <><Zap size={16} /> Scan for Hotspots</>}
            </button>
          </div>

          {error && <div className="alert alert-error">{error}</div>}

          {result && (
            <div className="card">
              <div className={styles.resultHeader}>
                <span className={`badge ${isNormal ? 'badge-green' : 'badge-red'}`} style={{ fontSize: '1rem', padding: '6px 18px' }}>
                  {result.fault_type}
                </span>
                <span style={{ color: 'var(--color-muted)', fontSize: '0.82rem' }}>
                  Confidence: <strong>{confidencePct}%</strong>
                </span>
              </div>
              <div className="grid-2" style={{ marginTop: '1rem' }}>
                <div className="metric-card">
                  <div className="metric-label">Result</div>
                  <div className="metric-value" style={{ fontSize: '1.2rem' }}>{result.fault_type}</div>
                </div>
                <div className={`metric-card ${isNormal ? '' : 'red'}`}>
                  <div className="metric-label">Confidence</div>
                  <div className="metric-value">{confidencePct}%</div>
                </div>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
