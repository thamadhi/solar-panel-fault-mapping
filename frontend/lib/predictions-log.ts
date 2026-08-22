'use client';

/*
 * Client-side prediction activity log.
 *
 * The Flask API has no /dashboard/stats or history endpoint, and the migration
 * constraint keeps the API untouched — so detections, localisations,
 * severities, and rectifications are recorded here (localStorage, per browser)
 * the moment a prediction succeeds. The Dashboard and Activity Log pages read
 * from this store.
 */

export interface PredictionEntry {
  id: string;
  created_at: string; // ISO timestamp
  source: string;     // page that produced it, e.g. "Fault Detection"
  mode: string;       // electrical | thermal | string_localization | hot_spot | rectification
  fault_type: string;
  confidence: number; // 0..1
}

export const LOG_KEY = 'pv_prediction_log';
const MAX_ENTRIES = 500;

type Listener = () => void;
const listeners = new Set<Listener>();

export function subscribeLog(listener: Listener): () => void {
  listeners.add(listener);
  return () => listeners.delete(listener);
}

function emit() {
  listeners.forEach(l => l());
}

export function getLog(): PredictionEntry[] {
  if (typeof window === 'undefined') return [];
  try {
    const raw = localStorage.getItem(LOG_KEY);
    return raw ? (JSON.parse(raw) as PredictionEntry[]) : [];
  } catch {
    return [];
  }
}

export function logPrediction(entry: Omit<PredictionEntry, 'id' | 'created_at'>) {
  if (typeof window === 'undefined') return;
  const full: PredictionEntry = {
    ...entry,
    id: `${Date.now()}-${Math.random().toString(36).slice(2, 8)}`,
    created_at: new Date().toISOString(),
  };
  const next = [full, ...getLog()].slice(0, MAX_ENTRIES);
  localStorage.setItem(LOG_KEY, JSON.stringify(next));
  emit();
}

export function clearLog() {
  if (typeof window === 'undefined') return;
  localStorage.removeItem(LOG_KEY);
  emit();
}

/* ── Aggregates for the dashboard ────────────────────────── */
export interface DashStats {
  total: number;
  avg_confidence: number | null;
  most_common_fault: string | null;
  recent: PredictionEntry[];
  trend: { day: string; count: number }[];
  distribution: { fault_type: string; count: number }[];
}

export function computeStats(entries: PredictionEntry[]): DashStats {
  const total = entries.length;
  const withConf = entries.filter(e => typeof e.confidence === 'number');
  const avg_confidence = withConf.length
    ? withConf.reduce((s, e) => s + e.confidence, 0) / withConf.length
    : null;

  const counts = new Map<string, number>();
  entries.forEach(e => counts.set(e.fault_type, (counts.get(e.fault_type) ?? 0) + 1));
  let most_common_fault: string | null = null;
  let best = 0;
  counts.forEach((n, k) => { if (n > best) { best = n; most_common_fault = k; } });

  const byDay = new Map<string, number>();
  entries.forEach(e => {
    const day = e.created_at.slice(0, 10);
    byDay.set(day, (byDay.get(day) ?? 0) + 1);
  });
  const trend = [...byDay.entries()]
    .sort((a, b) => a[0].localeCompare(b[0]))
    .map(([day, count]) => ({ day: day.slice(5), count }));

  const distribution = [...counts.entries()]
    .sort((a, b) => b[1] - a[1])
    .map(([fault_type, count]) => ({ fault_type, count }));

  return {
    total,
    avg_confidence,
    most_common_fault,
    recent: entries.slice(0, 10),
    trend,
    distribution,
  };
}
