'use client';

import { useRef, useState } from 'react';
import { localiseElectrical, localiseImage } from '@/lib/api';
import { logPrediction } from '@/lib/predictions-log';
import { MapPin, Zap, Image as ImageIcon, Crosshair } from 'lucide-react';
import styles from './page.module.css';

type Tab = 'csv' | 'image';

interface ElecResult {
  status: string;
  fault_type: string;
  confidence: number;
  faulty_strings: number[] | Record<string, unknown>[];
  location?: string;
  string_reliable?: boolean;
}

interface ImgResult {
  status: string;
  fault_type: string;
  confidence: number;
  location?: string;
  bounding_box?: number[] | { x_min?: number; y_min?: number; x_max?: number; y_max?: number };
  annotated_image?: string;
}

function parseCSV(text: string): Record<string, number>[] {
  const lines = text.trim().split('\n');
  const headers = lines[0].split(',').map(h => h.trim());
  return lines.slice(1).map(line => {
    const vals = line.split(',');
    const obj: Record<string, number> = {};
    headers.forEach((h, i) => { obj[h] = parseFloat(vals[i]?.trim() ?? '0'); });
    return obj;
  });
}

export default function LocalisationPage() {
  const [tab, setTab]               = useState<Tab>('csv');
  const [csvFile, setCsvFile]       = useState<File | null>(null);
  const [imgFile, setImgFile]       = useState<File | null>(null);
  const [imgPreview, setImgPreview] = useState<string | null>(null);
  const [elecResult, setElecResult] = useState<ElecResult | null>(null);
  const [imgResult, setImgResult]   = useState<ImgResult | null>(null);
  const [loading, setLoading]       = useState(false);
  const [error, setError]           = useState('');
  const fileRef = useRef<HTMLInputElement>(null);
  const imgRef  = useRef<HTMLInputElement>(null);

  async function handleCSVLocate() {
    if (!csvFile) return;
    setLoading(true); setError(''); setElecResult(null);
    try {
      const records = parseCSV(await csvFile.text());
      const data = (await localiseElectrical(records)) as ElecResult;
      setElecResult(data);
      logPrediction({
        source: 'Localisation',
        mode: 'string_localization',
        fault_type: String(data.fault_type),
        confidence: Number(data.confidence ?? 0),
      });
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Localisation failed');
    } finally { setLoading(false); }
  }

  function handleImageSelect(file: File) {
    setImgFile(file);
    setImgPreview(URL.createObjectURL(file));
    setImgResult(null); setError('');
  }

  async function handleImageLocate() {
    if (!imgFile) return;
    setLoading(true); setError(''); setImgResult(null);
    try {
      const data = (await localiseImage(imgFile)) as ImgResult;
      setImgResult(data);
      logPrediction({
        source: 'Localisation',
        mode: 'hotspot_localization',
        fault_type: String(data.fault_type),
        confidence: Number(data.confidence ?? 0),
      });
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Image localisation failed');
    } finally { setLoading(false); }
  }

  const isNormal = (r: ElecResult | ImgResult | null) =>
    !!r && (r.fault_type === 'Normal' || r.fault_type === 'Healthy' || /no fault/i.test(String(r.fault_type)));

  return (
    <div>
      <div className="page-title">📍 Fault Localisation</div>
      <div className="page-sub">STRING-LEVEL · HOTSPOT MAPPING</div>

      <div className="tabs-nav" style={{ marginBottom: '1.5rem' }}>
        <button className={`tab-btn ${tab === 'csv' ? 'active' : ''}`} onClick={() => { setTab('csv'); setError(''); }}>
          ⚡ Electrical Strings
        </button>
        <button className={`tab-btn ${tab === 'image' ? 'active' : ''}`} onClick={() => { setTab('image'); setError(''); }}>
          🖼️ Thermal Image
        </button>
      </div>

      {/* ── CSV Tab ── */}
      {tab === 'csv' && (
        <>
          <div className="card" style={{ marginBottom: '1rem' }}>
            <div className="alert alert-info" style={{ marginBottom: '1rem' }}>
              Upload inverter readings with the 32-string schema: <code>Vstr1(V)…Vstr32(V)</code>, <code>Istr1(A)…Istr32(A)</code> plus the 6 meta columns (<code>Ppv(W)</code>, temps). The CNN-BiLSTM model maps faults to specific strings.
            </div>
            <div
              className={`upload-zone ${csvFile ? styles.uploadActive : ''}`}
              onClick={() => fileRef.current?.click()}
            >
              <input ref={fileRef} type="file" accept=".csv,.xlsx,.xls" onChange={e => { if (e.target.files?.[0]) setCsvFile(e.target.files[0]); }} />
              <div className="upload-icon"><Zap size={36} color="var(--color-muted)" /></div>
              {csvFile ? (
                <div className="upload-label" style={{ color: 'var(--color-accent)', fontWeight: 600 }}>✓ {csvFile.name}</div>
              ) : (
                <>
                  <div className="upload-label">Click to upload electrical readings</div>
                  <div className="upload-hint">Supported: .csv</div>
                </>
              )}
            </div>
            <button
              className="btn btn-primary btn-full"
              style={{ marginTop: '1rem' }}
              disabled={!csvFile || loading}
              onClick={handleCSVLocate}
            >
              {loading ? <><span className="spinner" style={{ width:16, height:16, borderWidth:2 }} /> Locating…</> : <><MapPin size={16} /> Locate Faulty Strings</>}
            </button>
          </div>

          {error && <div className="alert alert-error">{error}</div>}

          {elecResult && (
            <div className="card">
              <div className={styles.resultHeader}>
                <span className={`badge ${isNormal(elecResult) ? 'badge-green' : 'badge-red'} ${styles.badgeLg}`}>
                  {elecResult.fault_type}
                </span>
                <div style={{ display: 'flex', gap: '0.75rem', flexWrap: 'wrap', alignItems: 'center' }}>
                  <span className="badge badge-blue">Confidence {(elecResult.confidence * 100).toFixed(1)}%</span>
                  {elecResult.location && <span className="badge badge-muted"><Crosshair size={11} /> {String(elecResult.location)}</span>}
                  <span className={`badge ${elecResult.string_reliable ? 'badge-green' : 'badge-yellow'}`}>
                    {elecResult.string_reliable ? 'Strings Reliable' : 'Strings Unreliable'}
                  </span>
                </div>
              </div>

              {Array.isArray(elecResult.faulty_strings) && elecResult.faulty_strings.length > 0 && (
                Number.isInteger(elecResult.faulty_strings[0]) ? (
                  <>
                    <div className="section-label">32-String Array Heatmap — red cells are faulty</div>
                    <div className={styles.stringGrid}>
                      {Array.from({ length: 32 }, (_, i) => i + 1).map(n => {
                        const faulty = (elecResult.faulty_strings as number[]).includes(n);
                        return (
                          <div key={n} className={`${styles.stringCell} ${faulty ? styles.cellFaulty : styles.cellHealthy}`}>
                            <span>S{n}</span>
                          </div>
                        );
                      })}
                    </div>
                  </>
                ) : (
                  <>
                    <div className="section-label">Faulty String Readings</div>
                    <div style={{ overflowX: 'auto' }}>
                      <table className="data-table">
                        <thead>
                          <tr>
                            <th>#</th>
                            {Object.keys(elecResult.faulty_strings[0] as Record<string, unknown>).map(k => <th key={k}>{k}</th>)}
                          </tr>
                        </thead>
                        <tbody>
                          {(elecResult.faulty_strings as Record<string, unknown>[]).slice(0, 32).map((row, i) => (
                            <tr key={i} className={styles.heatRow}>
                              <td>{i + 1}</td>
                              {Object.values(row).map((v, j) => (
                                <td key={j}>{typeof v === 'number' ? v.toFixed(3) : String(v)}</td>
                              ))}
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </>
                )
              )}
            </div>
          )}
        </>
      )}

      {/* ── Image Tab ── */}
      {tab === 'image' && (
        <>
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
                  <div className="upload-hint">Returns an annotated overlay with the hotspot region</div>
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
              onClick={handleImageLocate}
            >
              {loading ? <><span className="spinner" style={{ width:16, height:16, borderWidth:2 }} /> Processing…</> : <><MapPin size={16} /> Locate Hotspot Region</>}
            </button>
          </div>

          {error && <div className="alert alert-error">{error}</div>}

          {imgResult && (
            <div className="card">
              <div className={styles.resultHeader}>
                <span className={`badge ${isNormal(imgResult) ? 'badge-green' : 'badge-red'} ${styles.badgeLg}`}>
                  {imgResult.fault_type}
                </span>
                <div style={{ display: 'flex', gap: '0.75rem', flexWrap: 'wrap', alignItems: 'center' }}>
                  <span className="badge badge-blue">Confidence {(imgResult.confidence * 100).toFixed(1)}%</span>
                  {imgResult.location && <span className="badge badge-muted"><Crosshair size={11} /> {String(imgResult.location)}</span>}
                </div>
              </div>

              {imgResult.annotated_image && (
                <div style={{ marginTop: '1.25rem' }}>
                  <div className="section-label">Annotated Detection Overlay</div>
                  <div className={styles.annotated}>
                    {/* eslint-disable-next-line @next/next/no-img-element */}
                    <img src={`data:image/jpeg;base64,${imgResult.annotated_image}`} alt="Annotated thermal detection" />
                  </div>
                </div>
              )}

              {imgResult.bounding_box && (
                <div style={{ marginTop: '1rem' }}>
                  <div className="section-label">Bounding Box</div>
                  <div className="grid-4">
                    {(
                      Array.isArray(imgResult.bounding_box)
                        ? [['x', imgResult.bounding_box[0]], ['y', imgResult.bounding_box[1]], ['w', imgResult.bounding_box[2]], ['h', imgResult.bounding_box[3]]]
                        : [['x_min', (imgResult.bounding_box as Record<string, number>).x_min], ['y_min', (imgResult.bounding_box as Record<string, number>).y_min], ['x_max', (imgResult.bounding_box as Record<string, number>).x_max], ['y_max', (imgResult.bounding_box as Record<string, number>).y_max]]
                    ).map(([k, v]) => (
                      <div key={String(k)} className="metric-card">
                        <div className="metric-label">{k}</div>
                        <div className="metric-value" style={{ fontSize: '1.2rem' }}>{v != null ? Number(v).toFixed(1) : '—'}</div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </>
      )}
    </div>
  );
}
