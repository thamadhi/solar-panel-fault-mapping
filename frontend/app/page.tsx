'use client';

import Link from 'next/link';
import { Shield, MapPin, BarChart2, Wrench, ChevronRight, CheckCircle } from 'lucide-react';
import ThemeToggle from '@/components/ui/ThemeToggle';
import Logo from '@/components/ui/Logo';
import Typewriter from '@/components/fx/Typewriter';
import Reveal from '@/components/fx/Reveal';
import styles from './page.module.css';

const HEADLINES = [
  'Find the fault before it finds you.',
  'Your panels shouldn\u2019t hide problems.',
  'Detect faults before they become losses.',
  'See what your solar system is hiding.',
  'Smarter solar starts with knowing what\u2019s wrong.',
];

const FEATURES = [
  { icon: Shield,    title: 'Fault detection',  desc: 'Two independent readings — electrical signatures and thermal imagery — have to agree before anything gets flagged.' },
  { icon: MapPin,    title: 'Localisation',     desc: 'Pinpointed to the exact string or hotspot region, so nobody wanders the rows with a multimeter.' },
  { icon: BarChart2, title: 'Severity',         desc: 'A calibrated score that tells you whether it can wait for the next maintenance window — or can\u2019t.' },
  { icon: Wrench,    title: 'Rectification',    desc: 'A concrete fix with cost and downtime estimates attached. Not just \u201cinspect panel\u201d.' },
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
        <Link href="/" className={styles.navBrand} aria-label="OpenPVisor home">
          <Logo fontSize="1.2rem" />
        </Link>
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
        <h1 className={styles.heroTitle}>
          <span className={styles.visuallyHidden}>
            Find the fault before it finds you.
          </span>
          <span className={styles.heroGhost} aria-hidden="true">
            {HEADLINES.reduce((a, b) => (b.length > a.length ? b : a))}
          </span>
          <Typewriter phrases={HEADLINES} />
        </h1>
        <p className={styles.heroSub}>
          OpenPVisor keeps an eye on every string in your array — cross-checking electrical
          signals against thermal imagery — then tells you what failed, where it is,
          and how much it matters.
        </p>
        <div className={styles.heroCtas}>
          <Link href="/auth" className="btn btn-primary btn-lg">
            Enter Dashboard <ChevronRight size={18} />
          </Link>
          <a href="#features" className="btn btn-outline btn-lg">
            See how it works
          </a>
        </div>
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
          <p className={styles.sectionEyebrow}>What we do</p>
          <h2>Spot it. Place it.<br />Size it up. Fix it.</h2>
        </div>
        <div className="grid-4">
          {FEATURES.map(({ icon: Icon, title, desc }, i) => (
            <Reveal key={title} delay={i * 100}>
              <div className={`card ${styles.featureCard}`}>
                <div className={styles.featureTop}>
                  <span className={styles.featureIndex}>{String(i + 1).padStart(2, '0')}</span>
                  <Icon size={20} strokeWidth={1.8} />
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
              <h2>Built alongside the people who walk the rows.</h2>
              <p>
                OpenPVisor Insight grew out of field work on real plants. Every prediction is
                traced back to its evidence, and every screen was shaped by long conversations
                with the engineers, operators, and technicians who use it at 7am.
              </p>
              <ul className={styles.checkList}>
                {['Multi-role access, properly authenticated', 'An explanation behind every prediction',
                  'Answers in plain language, on call', 'Full prediction history & trend analytics'].map(t => (
                  <li key={t}><CheckCircle size={16} color="var(--color-accent)" /> {t}</li>
                ))}
              </ul>
              <Link href="/auth" className="btn btn-primary" style={{ marginTop: '1.5rem', display: 'inline-flex' }}>
                Get Started <ChevronRight size={16} />
              </Link>
            </div>
          </Reveal>
          <Reveal delay={140}>
            <div className={`card ${styles.missionCard}`}>
              <div className={styles.missionHead}>
                <span>Our mission</span>
                <span className={styles.missionNote}>why OpenPVisor exists</span>
              </div>
              <p className={styles.missionStatement}>
                Solar fails quietly — a hotspot here, a drifting string there,
                nothing you can see from the ground. We exist to catch those
                failures while they&rsquo;re still cheap: every panel accounted
                for, every fault explained in plain language.
              </p>
              <ul className={styles.missionValues}>
                {['No black-box predictions',
                  'Efficient fault diagnosis',
                  'Downtime is the real enemy'].map(v => (
                  <li key={v}>{v}</li>
                ))}
              </ul>
            </div>
          </Reveal>
        </div>
      </section>

      {/* ── Footer ── */}
      <footer className={styles.footer}>
        <span className={styles.footerRule} aria-hidden="true" />
        <span>An OpenPVisor product</span>
      </footer>
    </div>
  );
}
