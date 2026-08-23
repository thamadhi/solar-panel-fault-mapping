import axios from 'axios';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000';

const api = axios.create({
  baseURL: API_BASE,
  timeout: 180_000,
});

// Attach JWT from localStorage on every request
api.interceptors.request.use((config) => {
  if (typeof window !== 'undefined') {
    const token = localStorage.getItem('pv_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
  }
  return config;
});

/* ── Auth ──────────────────────────────────────────────── */
export async function apiLogin(username: string, password: string) {
  const res = await api.post('/auth/login', { username, password });
  return res.data as {
    status: string;
    token: string;
    user: { id: number; username: string; email: string; type: string };
  };
}

export async function apiRegister(username: string, email: string, password: string, userType: string) {
  const res = await api.post('/auth/register', { username, email, password, user_type: userType });
  return res.data as {
    status: string;
    token: string;
    user: { id: number; username: string; email: string; type: string };
  };
}

/* ── Fault Detection ────────────────────────────────────── */
export async function predictElectrical(records: object[]) {
  const res = await api.post('/predict', records);
  return res.data;
}

export async function predictImage(file: File) {
  const form = new FormData();
  form.append('image', file);
  const res = await api.post('/predict-image', form, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return res.data;
}

/* ── Explainability ─────────────────────────────────────── */
export async function explainElectrical(records: object[], rowIdx: number) {
  const res = await api.post('/explain/electrical', { records, row_idx: rowIdx });
  return res.data;
}

/* ── Localisation ───────────────────────────────────────── */
export async function localiseElectrical(data: object[]) {
  const res = await api.post('/localise', data);
  return res.data;
}

export async function localiseImage(file: File) {
  const form = new FormData();
  form.append('image', file);
  const res = await api.post('/localise', form, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return res.data;
}

/* ── Rectification ──────────────────────────────────────── */
export async function rectifyFault(data: object) {
  const res = await api.post('/rectify', data);
  return res.data;
}

/* ── Assistant ──────────────────────────────────────────── */
export async function assistantChat(message: string, page: string, pageData?: object) {
  const res = await api.post('/assistant/chat', { message, page, page_data: pageData });
  return res.data;
}

export async function assistantHistory() {
  const res = await api.get('/assistant/history');
  return res.data;
}

export default api;
