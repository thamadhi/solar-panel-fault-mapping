'use client';

import Link from 'next/link';
import { Shield, MapPin, BarChart2, Wrench, Sun, ChevronRight, Zap, CheckCircle, Globe } from 'lucide-react';
import ThemeToggle from '@/components/ui/ThemeToggle';
import Reveal from '@/components/fx/Reveal';
import styles from './page.module.css';

const FEATURES = [
  { icon: Shield,   title: 'Fault Detection',  desc: 'Instantly spot electrical & thermal problems in your solar system using AI-powered models.' },
  { icon: MapPin,   title: 'Localisation',     desc: 'See exactly where the issue is — faulty strings or hotspot regions on thermal images.' },
  { icon: BarChart2,title: 'Severity',          desc: 'Understand how serious the problem is and get a quantified severity score.' },
  { icon: Wrench,   title: 'Rectification',    desc: 'Receive intelligent recommendations to fix issues with cost and downtime estimates.' },
];

const STATS = [
  { value: '99.2%', label: 'Detection Accuracy' },
  { value: '< 2s',  label: 'Analysis Time' },
  { value: '32',    label: 'Strings Monitored' },
  { value: '4',     label: 'Fault Types Classified' },
];

export default function LandingPage() {
  return (
    <div className={styles.page}>
      {/* ── Navbar ── */}
      <nav className={styles.nav}>
        <div className={styles.navBrand}>
          <Sun size={26} color="var(--color-accent)" strokeWidth={2.5} />
          <span>OpenPVisor Insight</span>
        </div>
        <div className={styles.navLinks}>
          <a href="#features" className={styles.navLink}>Features</a>
          <a href="#about"    className={styles.navLink}>About</a>
          <a href="#stats"    className={styles.navLink}>Stats</a>
        </div>
        <div className={styles.navActions}>
          <ThemeToggle />
          <Link href="/auth" className="btn btn-primary btn-sm">
            Operator Log In
          </Link>
        </div>
      </nav>

      {/* ── Hero ── */}
      <section className={styles.hero}>
        <div className={styles.heroBadge}>
          <Zap size={12} />
          AI-Powered Solar Intelligence
        </div>
        <h1 className={styles.heroTitle}>
          Future-Proof<br />
          <span className={`gradient-text ${styles.heroAccent}`}>Solar Assets.</span>
        </h1>
        <p className={styles.heroSub}>
          OpenPVisor Insight helps you detect, locate, and fix solar panel faults quickly and accurately —
          combining electrical analysis and computer vision in one intelligent dashboard.
        </p>
        <div className={styles.heroCtas}>
          <Link href="/auth" className="btn btn-primary btn-lg">
            Enter Dashboard <ChevronRight size={18} />
          </Link>
          <a href="#features" className="btn btn-outline btn-lg">
            Learn More
          </a>
        </div>
        <div className={styles.heroGlow} />
      </section>

      {/* ── Stats ── */}
      <section className={styles.stats} id="stats">
        {STATS.map((s, i) => (
          <Reveal key={s.label} delay={i * 90}>
            <div className={styles.statItem}>
              <div className={styles.statValue}>{s.value}</div>
              <div className={styles.statLabel}>{s.label}</div>
            </div>
          </Reveal>
        ))}
      </section>

      {/* ── Features ── */}
      <section className={styles.features} id="features">
        <div className={styles.sectionHeader}>
          <p className={styles.sectionEyebrow}>What We Do</p>
          <h2>Everything You Need to Protect Your Solar Investment</h2>
        </div>
        <div className="grid-4">
          {FEATURES.map(({ icon: Icon, title, desc }, i) => (
            <Reveal key={title} delay={i * 100}>
              <div className={`card ${styles.featureCard}`}>
                <div className={styles.featureIcon}>
                  <Icon size={28} strokeWidth={1.8} />
                </div>
                <h3>{title}</h3>
                <p>{desc}</p>
              </div>
            </Reveal>
          ))}
        </div>
      </section>

      {/* ── About ── */}
      <section className={styles.about} id="about">
        <div className={styles.aboutGrid}>
          <Reveal>
            <div className={styles.aboutText}>
              <p className={styles.sectionEyebrow}>About OpenPVisor</p>
              <h2>Built for Solar Engineers, Operators &amp; Technicians</h2>
              <p>
                OpenPVisor Insight is an end-to-end fault management platform combining Random Forest
                electrical classification, CNN-BiLSTM string localisation, XGBoost severity
                scoring, and Score-CAM thermal hotspot detection — all in one unified dashboard.
              </p>
              <ul className={styles.checkList}>
                {['JWT-authenticated multi-role access', 'SHAP explainability for every prediction',
                  'Real-time AI assistant chatbot', 'Full prediction history & trend analytics'].map(t => (
                  <li key={t}><CheckCircle size={16} color="var(--color-accent)" /> {t}</li>
                ))}
              </ul>
              <Link href="/auth" className="btn btn-primary" style={{ marginTop: '1.5rem', display: 'inline-flex' }}>
                Get Started <ChevronRight size={16} />
              </Link>
            </div>
          </Reveal>
          <div className={styles.aboutCards}>
            {[
              { Icon: Globe, title: 'Our Mission', desc: 'Making solar energy more efficient through AI-powered fault detection.' },
              { Icon: Sun,   title: 'Our Vision',  desc: 'A world where solar energy is maximized through intelligent monitoring.' },
            ].map(({ Icon, title, desc }, i) => (
              <Reveal key={title} delay={i * 120}>
                <div className={`card ${styles.aboutCard}`}>
                  <Icon size={32} color="var(--color-accent)" strokeWidth={1.8} />
                  <h3>{title}</h3>
                  <p>{desc}</p>
                </div>
              </Reveal>
            ))}
          </div>
        </div>
      </section>

      {/* ── Footer ── */}
      <footer className={styles.footer}>
        <Sun size={18} color="var(--color-accent)" />
        <span>AN OPENPVISOR PRODUCT</span>
      </footer>
    </div>
  );
}
