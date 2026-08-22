'use client';

import { useEffect, useState } from 'react';
import {
  computeStats, getLog, subscribeLog,
  type DashStats,
} from '@/lib/predictions-log';
import {
  LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer, Legend,
} from 'recharts';
import styles from './page.module.css';

type ActiveTab = 'latest' | 'trends' | 'distribution' | 'analytics';

export default function DashboardPage() {
  const [stats, setStats] = useState<DashStats>(() => computeStats([]));
  const [activeTab, setActiveTab] = useState<ActiveTab>('latest');

  // Live updates: recompute whenever a page logs a new prediction
  useEffect(() => {
    const update = () => setStats(computeStats(getLog()));
    update();
    return subscribeLog(update);
  }, []);

  const METRICS = [
    { label: 'Total Detections',  value: stats?.total ?? 0,       color: '',       },
    { label: 'Avg. Confidence',   value: stats?.avg_confidence != null ? `${(stats.avg_confidence * 100).toFixed(1)}%` : 'N/A', color: 'blue',  },
    { label: 'Most Common Fault', value: stats?.most_common_fault ?? 'N/A',        color: 'yellow', },
    { label: 'System Status',     value: 'Online',                color: '',       },
  ];

  return (
    <div>
      <div className="page-title">📊 Dashboard</div>
      <div className="page-sub">SOLAR PV INTELLIGENCE OVERVIEW</div>

      {/* Metrics */}
      <div className="grid-4" style={{ marginBottom: '2rem' }}>
        {METRICS.map(({ label, value, color }) => (
          <div key={label} className={`metric-card ${color}`}>
            <div className="metric-label">{label}</div>
            <div className="metric-value">{String(value)}</div>
          </div>
        ))}
      </div>

      <hr />

      {/* Tabs */}
      <div className="tabs-nav" style={{ marginBottom: '1.5rem' }}>
        {(['latest', 'trends', 'distribution', 'analytics'] as ActiveTab[]).map(t => (
          <button key={t} className={`tab-btn ${activeTab === t ? 'active' : ''}`} onClick={() => setActiveTab(t)}>
            {{ latest: '🕒 Latest', trends: '📈 Trends', distribution: '🧩 Distribution', analytics: '📊 Analytics' }[t]}
          </button>
        ))}
      </div>

      {/* Tab content */}
      {activeTab === 'latest' && (
        <div className="card">
          {(!stats?.recent || stats.recent.length === 0) ? (
            <div className="alert alert-info">No predictions yet. Run a fault detection to see data here.</div>
          ) : (
            <div style={{ overflowX: 'auto' }}>
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Time</th><th>Source</th><th>Mode</th><th>Fault Type</th><th>Confidence</th>
                  </tr>
                </thead>
                <tbody>
                  {stats.recent.map(p => (
                    <tr key={p.id}>
                      <td>{new Date(p.created_at).toLocaleString()}</td>
                      <td>{p.source}</td>
                      <td>{p.mode}</td>
                      <td>
                        <span className={`badge ${p.fault_type === 'Normal' ? 'badge-green' : 'badge-red'}`}>
                          {p.fault_type}
                        </span>
                      </td>
                      <td>{p.confidence != null ? `${(p.confidence * 100).toFixed(1)}%` : '—'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      {activeTab === 'trends' && (
        <div className="card">
          <h3 style={{ marginBottom: '1rem' }}>Daily Detection Trend</h3>
          {(!stats?.trend || stats.trend.length === 0) ? (
            <div className="alert alert-info">No trend data yet.</div>
          ) : (
            <ResponsiveContainer width="100%" height={320}>
              <LineChart data={stats.trend}>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" />
                <XAxis dataKey="day" tick={{ fontSize: 11 }} />
                <YAxis tick={{ fontSize: 11 }} />
                <Tooltip />
                <Line type="monotone" dataKey="count" stroke="var(--color-accent)" strokeWidth={3} dot={{ fill: 'var(--color-accent)' }} />
              </LineChart>
            </ResponsiveContainer>
          )}
        </div>
      )}

      {activeTab === 'distribution' && (
        <div className="card">
          <h3 style={{ marginBottom: '1rem' }}>Fault Type Distribution</h3>
          {(!stats?.distribution || stats.distribution.length === 0) ? (
            <div className="alert alert-info">No distribution data yet.</div>
          ) : (
            <ResponsiveContainer width="100%" height={320}>
              <BarChart data={stats.distribution}>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" />
                <XAxis dataKey="fault_type" tick={{ fontSize: 11 }} />
                <YAxis tick={{ fontSize: 11 }} />
                <Tooltip />
                <Bar dataKey="count" fill="var(--color-accent)" radius={[4,4,0,0]} />
              </BarChart>
            </ResponsiveContainer>
          )}
        </div>
      )}

      {activeTab === 'analytics' && (
        <div className={styles.analytics}>
          <div className="card">
            <h3 style={{ marginBottom: '1rem' }}>Electrical vs Thermal Mode</h3>
            {(!stats?.distribution || stats.distribution.length === 0) ? (
              <div className="alert alert-info">No analytics data yet.</div>
            ) : (
              <ResponsiveContainer width="100%" height={260}>
                <BarChart data={stats.distribution}>
                  <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" />
                  <XAxis dataKey="fault_type" tick={{ fontSize: 11 }} />
                  <YAxis tick={{ fontSize: 11 }} />
                  <Tooltip />
                  <Legend />
                  <Bar dataKey="count" fill="var(--color-info)" radius={[4,4,0,0]} />
                </BarChart>
              </ResponsiveContainer>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
