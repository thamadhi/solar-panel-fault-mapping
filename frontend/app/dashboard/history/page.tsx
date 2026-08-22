'use client';

import { useEffect, useState } from 'react';
import { getLog, clearLog, subscribeLog, type PredictionEntry } from '@/lib/predictions-log';
import { History as HistoryIcon, Trash2, Download } from 'lucide-react';

export default function HistoryPage() {
  const [entries, setEntries] = useState<PredictionEntry[]>(() => []);

  useEffect(() => {
    const update = () => setEntries(getLog());
    update();
    return subscribeLog(update);
  }, []);

  function exportCSV() {
    const header = 'time,source,mode,fault_type,confidence\n';
    const rows = entries.map(e =>
      `${e.created_at},${e.source},${e.mode},"${String(e.fault_type).replace(/"/g, '""')}",${e.confidence}`
    ).join('\n');
    const url = URL.createObjectURL(new Blob([header + rows], { type: 'text/csv' }));
    const a = document.createElement('a');
    a.href = url;
    a.download = `pv-activity-log-${new Date().toISOString().slice(0, 10)}.csv`;
    a.click();
    URL.revokeObjectURL(url);
  }

  return (
    <div>
      <div className="page-title">🕓 Activity Log</div>
      <div className="page-sub">RECENT PREDICTIONS FROM THIS BROWSER</div>

      <div className="card">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: '1rem', marginBottom: '1rem', flexWrap: 'wrap' }}>
          <span className="badge badge-muted"><HistoryIcon size={12} /> {entries.length} record{entries.length === 1 ? '' : 's'}</span>
          <div style={{ display: 'flex', gap: '0.5rem' }}>
            <button className="btn btn-outline btn-sm" onClick={exportCSV} disabled={!entries.length}>
              <Download size={13} /> Export CSV
            </button>
            <button className="btn btn-danger btn-sm" onClick={() => { if (confirm('Clear the activity log?')) clearLog(); }} disabled={!entries.length}>
              <Trash2 size={13} /> Clear Log
            </button>
          </div>
        </div>

        {entries.length === 0 ? (
          <div className="alert alert-info">
            No predictions recorded yet. Run Fault Detection, Localisation, Severity or Rectification and results will appear here.
          </div>
        ) : (
          <div style={{ overflowX: 'auto' }}>
            <table className="data-table">
              <thead>
                <tr>
                  <th>#</th><th>Time</th><th>Source</th><th>Mode</th><th>Fault Type</th><th>Confidence</th>
                </tr>
              </thead>
              <tbody>
                {entries.map((p, i) => (
                  <tr key={p.id}>
                    <td>{i + 1}</td>
                    <td>{new Date(p.created_at).toLocaleString()}</td>
                    <td>{p.source}</td>
                    <td><span className="badge badge-muted">{p.mode}</span></td>
                    <td>
                      <span className={`badge ${/normal|healthy|no fault/i.test(String(p.fault_type)) ? 'badge-green' : 'badge-red'}`}>
                        {p.fault_type}
                      </span>
                    </td>
                    <td>{typeof p.confidence === 'number' ? `${(p.confidence * 100).toFixed(1)}%` : '—'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
