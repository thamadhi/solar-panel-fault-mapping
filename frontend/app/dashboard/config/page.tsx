'use client';

import { useState, useSyncExternalStore } from 'react';
import { createLocalStore } from '@/lib/localStore';
import { Save, CheckCircle } from 'lucide-react';
import styles from './page.module.css';

const SYSTEM_TYPES = ['Solar Farm', 'Grid-Tied', 'Off-Grid', 'Hybrid'];

interface PvConfig {
  system_type: string;
  modules_per_string: number;
}

const configStore = createLocalStore<PvConfig>('pv_system_config', JSON.parse);

export default function ConfigPage() {
  const saved       = useSyncExternalStore(configStore.subscribe, configStore.getSnapshot, configStore.getServerSnapshot);
  const [systemType, setSystemType]    = useState(saved?.system_type ?? 'Solar Farm');
  const [modulesPerString, setModules] = useState(saved?.modules_per_string ?? 1);
  const [flash, setFlash]              = useState('');

  function handleSave(e: React.FormEvent) {
    e.preventDefault();
    configStore.set({ system_type: systemType, modules_per_string: modulesPerString });
    setFlash('PV system configuration saved.');
    setTimeout(() => setFlash(''), 3000);
  }

  return (
    <div>
      <div className="page-title">⚙️ PV System Config</div>
      <div className="page-sub">INSTALLATION PROFILE</div>

      <form onSubmit={handleSave}>
        <div className="card" style={{ maxWidth: 560 }}>
          <div className="alert alert-info" style={{ marginBottom: '1.25rem' }}>
            Configuration is stored for this browser — the API has no config endpoint.
          </div>

          <div className="form-group">
            <label className="form-label">System Type</label>
            <select className="form-select" value={systemType} onChange={e => setSystemType(e.target.value)}>
              {SYSTEM_TYPES.map(t => <option key={t} value={t}>{t}</option>)}
            </select>
          </div>

          <div className="form-group">
            <label className="form-label">Modules per String</label>
            <input
              className="form-input"
              type="number"
              min={1}
              max={1000}
              step={1}
              value={modulesPerString}
              onChange={e => setModules(Math.max(1, parseInt(e.target.value || '1', 10)))}
            />
          </div>

          {flash && <div className="alert alert-success" style={{ marginBottom: '1rem' }}><CheckCircle size={14} /> {flash}</div>}

          <button type="submit" className="btn btn-primary btn-full">
            <Save size={15} /> Save PV System
          </button>
        </div>
      </form>

      <div className="section-label" style={{ maxWidth: 560 }}>Current Configuration</div>
      <div className="card" style={{ maxWidth: 560 }}>
        {saved ? (
          <div className={styles.configSummary}>
            <div><span>System Type</span><strong>{saved.system_type}</strong></div>
            <div><span>Modules per String</span><strong>{saved.modules_per_string}</strong></div>
          </div>
        ) : (
          <div className="alert alert-warning">No configuration saved yet.</div>
        )}
      </div>
    </div>
  );
}
