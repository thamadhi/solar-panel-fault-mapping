'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/lib/AuthContext';
import { apiLogin, apiRegister } from '@/lib/api';
import Logo from '@/components/ui/Logo';
import { LogIn, UserPlus } from 'lucide-react';
import styles from './page.module.css';
import type { AxiosError } from 'axios';

type Tab = 'login' | 'register';

const REGISTRATION_ROLES = ['Standard', 'Solar PV Operator', 'Technician'];

function apiErrorMessage(err: unknown, fallback: string): string {
  const axiosErr = err as AxiosError<{ message?: string }>;
  return axiosErr?.response?.data?.message ?? fallback;
}

export default function AuthPage() {
  const [tab, setTab]         = useState<Tab>('login');
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError]     = useState('');
  const [loading, setLoading] = useState(false);
  const { login, isAuthenticated } = useAuth();
  const router      = useRouter();

  // Already hold a valid, unexpired session (e.g. the tab was closed and
  // reopened) — skip the form and go straight to the dashboard instead of
  // making a returning user log in again.
  useEffect(() => {
    if (isAuthenticated) router.replace('/dashboard');
  }, [isAuthenticated, router]);

  // Register form state
  const [regUsername, setRegUsername]   = useState('');
  const [regEmail, setRegEmail]         = useState('');
  const [regPassword, setRegPassword]   = useState('');
  const [regConfirm, setRegConfirm]     = useState('');
  const [regRole, setRegRole]           = useState('Standard');

  function afterAuth(data: { status: string; token: string; user: Parameters<typeof login>[1] }) {
    if (data.status === 'success') {
      login(data.token, data.user);
      router.replace('/dashboard');
      return true;
    }
    return false;
  }

  async function handleLogin(e: React.FormEvent) {
    e.preventDefault();
    setError(''); setLoading(true);
    try {
      const data = await apiLogin(username.trim(), password);
      if (!afterAuth(data)) setError('Invalid credentials. Please try again.');
    } catch (err: unknown) {
      setError(apiErrorMessage(err, 'Cannot reach the API server. Make sure it is running.'));
    } finally { setLoading(false); }
  }

  async function handleRegister(e: React.FormEvent) {
    e.preventDefault();
    setError('');

    if (regUsername.trim().length < 3) { setError('Username must be at least 3 characters.'); return; }
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(regEmail.trim())) { setError('Please enter a valid email address.'); return; }
    if (regPassword.length < 8) { setError('Password must be at least 8 characters.'); return; }
    if (regPassword !== regConfirm) { setError('Passwords do not match.'); return; }

    setLoading(true);
    try {
      const data = await apiRegister(regUsername.trim(), regEmail.trim(), regPassword, regRole);
      if (!afterAuth(data)) setError('Registration failed. Please try again.');
    } catch (err: unknown) {
      setError(apiErrorMessage(err, 'Cannot reach the API server. Make sure it is running.'));
    } finally { setLoading(false); }
  }

  // Branded hold instead of flashing the login form while the redirect above
  // takes effect.
  if (isAuthenticated) {
    return (
      <div className="splash">
        <div className="splashLogo">
          <Logo fontSize="clamp(1.15rem, 4vw, 1.6rem)" />
        </div>
        <div className="splashBar" />
        <div className="splashText">Already signed in…</div>
      </div>
    );
  }

  return (
    <div className={styles.page}>
      <div className={styles.card}>
        {/* Brand */}
        <div className={styles.brand}>
          <h1>
            <Logo fontSize="1.6rem" />
          </h1>
          <p>Solar Intelligence Hub</p>
        </div>

        {/* Tabs */}
        <div className="tabs-nav" style={{ marginBottom: '1.5rem' }}>
          <button className={`tab-btn ${tab === 'login' ? 'active' : ''}`} onClick={() => { setTab('login'); setError(''); }}>
            <LogIn size={14} style={{ display: 'inline', marginRight: 4 }} /> Login
          </button>
          <button className={`tab-btn ${tab === 'register' ? 'active' : ''}`} onClick={() => { setTab('register'); setError(''); }}>
            <UserPlus size={14} style={{ display: 'inline', marginRight: 4 }} /> Register
          </button>
        </div>

        {error && <div className="alert alert-error" style={{ marginBottom: '1rem' }}>{error}</div>}

        {tab === 'login' ? (
          <form onSubmit={handleLogin} className={styles.form}>
            <div className="form-group">
              <label className="form-label">Username</label>
              <input
                className="form-input"
                type="text"
                placeholder="Enter your username"
                value={username}
                onChange={e => setUsername(e.target.value)}
                required
                autoFocus
              />
            </div>
            <div className="form-group">
              <label className="form-label">Password</label>
              <input
                className="form-input"
                type="password"
                placeholder="Enter your password"
                value={password}
                onChange={e => setPassword(e.target.value)}
                required
              />
            </div>
            <button type="submit" className="btn btn-primary btn-full" disabled={loading}>
              {loading ? <span className="spinner" style={{ width:16, height:16, borderWidth:2 }} /> : <LogIn size={16} />}
              {loading ? 'Signing in…' : 'Sign In'}
            </button>
          </form>
        ) : (
          <form onSubmit={handleRegister} className={styles.form}>
            <div className="form-group">
              <label className="form-label">Username</label>
              <input
                className="form-input"
                type="text"
                placeholder="Choose a username (min 3 chars)"
                value={regUsername}
                onChange={e => setRegUsername(e.target.value)}
                required
                autoFocus
              />
            </div>
            <div className="form-group">
              <label className="form-label">Email</label>
              <input
                className="form-input"
                type="email"
                placeholder="you@example.com"
                value={regEmail}
                onChange={e => setRegEmail(e.target.value)}
                required
              />
            </div>
            <div className="grid-2" style={{ gap: '0.75rem' }}>
              <div className="form-group">
                <label className="form-label">Password</label>
                <input
                  className="form-input"
                  type="password"
                  placeholder="Min 8 characters"
                  value={regPassword}
                  onChange={e => setRegPassword(e.target.value)}
                  required
                />
              </div>
              <div className="form-group">
                <label className="form-label">Confirm Password</label>
                <input
                  className="form-input"
                  type="password"
                  placeholder="Repeat password"
                  value={regConfirm}
                  onChange={e => setRegConfirm(e.target.value)}
                  required
                />
              </div>
            </div>
            <div className="form-group">
              <label className="form-label">Account Type</label>
              <select className="form-select" value={regRole} onChange={e => setRegRole(e.target.value)}>
                {REGISTRATION_ROLES.map(r => <option key={r} value={r}>{r}</option>)}
              </select>
            </div>
            <button type="submit" className="btn btn-primary btn-full" disabled={loading}>
              {loading ? <span className="spinner" style={{ width:16, height:16, borderWidth:2 }} /> : <UserPlus size={16} />}
              {loading ? 'Creating account…' : 'Create Account'}
            </button>
          </form>
        )}

        <p className={styles.back} onClick={() => router.push('/')}>← Back to Home</p>
      </div>
    </div>
  );
}
