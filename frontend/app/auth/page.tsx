'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/lib/AuthContext';
import { apiLogin } from '@/lib/api';
import { Sun, LogIn, UserPlus } from 'lucide-react';
import styles from './page.module.css';

type Tab = 'login' | 'register';

export default function AuthPage() {
  const [tab, setTab]         = useState<Tab>('login');
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError]     = useState('');
  const [loading, setLoading] = useState(false);
  const { login }   = useAuth();
  const router      = useRouter();

  async function handleLogin(e: React.FormEvent) {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      const data = await apiLogin(username.trim(), password);
      if (data.status === 'success') {
        login(data.token, data.user);
        router.replace('/dashboard');
      } else {
        setError('Invalid credentials. Please try again.');
      }
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Login failed';
      setError(msg.includes('401') ? 'Invalid username or password.' : 'Cannot reach the API server. Make sure it is running.');
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className={styles.page}>
      <div className={styles.card}>
        {/* Brand */}
        <div className={styles.brand}>
          <Sun size={36} color="var(--color-accent)" strokeWidth={2} />
          <h1>OpenPVisor Insight</h1>
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
            {error && <div className="alert alert-error">{error}</div>}
            <button type="submit" className="btn btn-primary btn-full" disabled={loading}>
              {loading ? <span className="spinner" style={{ width:16, height:16, borderWidth:2 }} /> : <LogIn size={16} />}
              {loading ? 'Signing in…' : 'Sign In'}
            </button>
          </form>
        ) : (
          <div className={styles.registerInfo}>
            <div className="alert alert-info">
              New accounts are created by your system administrator. Contact them to receive your credentials.
            </div>
            <p>Once you have credentials, switch to the <strong>Login</strong> tab to access the dashboard.</p>
          </div>
        )}

        <p className={styles.back} onClick={() => router.push('/')}>← Back to Home</p>
      </div>
    </div>
  );
}
