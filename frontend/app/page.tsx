'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import {
  Shield, MapPin, BarChart2, Wrench, ChevronRight, CheckCircle,
  EyeOff, ArrowRight, ExternalLink, Mail,
} from 'lucide-react';
import ThemeToggle from '@/components/ui/ThemeToggle';
import Logo from '@/components/ui/Logo';
import Typewriter from '@/components/fx/Typewriter';
import Reveal from '@/components/fx/Reveal';
import Sunburst from '@/components/marketing/Sunburst';
import ProductPreview from '@/components/marketing/ProductPreview';
import LandingAssistant from '@/components/chat/LandingAssistant';
import styles from './page.module.css';

const HEADLINES = [
  'Find the fault before it finds you.',
  'Your panels shouldn’t hide problems.',
  'Detect faults before they become losses.',
  'See what your solar system is hiding.',
  'Smarter solar starts with knowing what’s wrong.',
];

const FEATURES = [
  { icon: Shield,    title: 'Fault detection',  desc: 'Two independent readings — electrical signatures and thermal imagery — have to agree before anything gets flagged.' },
  { icon: MapPin,    title: 'Localisation',     desc: 'Pinpointed to the exact string or hotspot region, so nobody wanders the rows with a multimeter.' },
  { icon: BarChart2, title: 'Severity',         desc: 'A calibrated score that tells you whether it can wait for the next maintenance window — or can’t.' },
  { icon: Wrench,    title: 'Rectification',    desc: 'A concrete fix with cost and downtime estimates attached. Not just “inspect panel”.' },
];

const STATS = [
  { value: '99.2%', label: 'Detection Accuracy' },
  { value: '< 2s',  label: 'Analysis Time' },
  { value: '32',    label: 'Strings Monitored' },
  { value: '4',     label: 'Fault Types Classified' },
];

const TECH = ['Python', 'TensorFlow', 'XGBoost', 'scikit-learn', 'Flask', 'Next.js', 'Docker'];

export default function LandingPage() {
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 12);
    onScroll();
    window.addEventListener('scroll', onScroll, { passive: true });
    return () => window.removeEventListener('scroll', onScroll);
  }, []);

  return (
    <div className={styles.page}>
      {/* ── Navbar ── */}
      <nav className={`${styles.nav} ${scrolled ? styles.navScrolled : ''}`}>
        <Link href="/" className={styles.navBrand} aria-label="OpenSunray home">
          <Logo fontSize="1.2rem" />
        </Link>
        <div className={styles.navLinks}>
          <a href="#problem"  className={styles.navLink}>The Problem</a>
          <a href="#features" className={styles.navLink}>How it works</a>
          <a href="#preview"  className={styles.navLink}>Product</a>
          <a href="#about"    className={styles.navLink}>About</a>
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
        <div className={styles.heroGrid}>
          <div className={styles.heroCol}>
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
              OpenSunray keeps an eye on every string in your array — cross-checking electrical
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
          </div>
          <div className={styles.heroCol}>
            <Sunburst />
          </div>
        </div>
      </section>

      {/* ── Problem ── */}
      <section className={styles.problem} id="problem">
        <Reveal>
          <div className={styles.problemGrid}>
            <div>
              <p className={styles.sectionEyebrow}>The problem</p>
              <h2>Solar doesn&rsquo;t fail loudly.</h2>
              <p className={styles.problemLede}>
                No broken glass. No warning light. No obvious sign — just a small fault quietly
                reducing energy production, day after day. Finding it the traditional way means
                walking rows of panels, checking measurements, and piecing together a thermal
                image by hand.
              </p>
            </div>
            <div className={styles.panelRow} aria-hidden="true">
              {Array.from({ length: 8 }).map((_, i) => (
                <span key={i} className={`${styles.panelCell} ${i === 4 ? styles.panelCellFault : ''}`} />
              ))}
            </div>
          </div>
        </Reveal>
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

      {/* ── How it works ── */}
      <section className={styles.features} id="features">
        <div className={styles.sectionHeader}>
          <p className={styles.sectionEyebrow}>How it works</p>
          <h2>Spot it. Place it.<br />Size it up. Fix it.</h2>
        </div>
        <div className={styles.stepFlow}>
          {FEATURES.map(({ icon: Icon, title, desc }, i) => (
            <Reveal key={title} delay={i * 100} className={styles.stepWrap}>
              <div className={`card ${styles.featureCard}`}>
                <div className={styles.featureTop}>
                  <span className={styles.featureIndex}>{String(i + 1).padStart(2, '0')}</span>
                  <Icon size={20} strokeWidth={1.8} />
                </div>
                <h3>{title}</h3>
                <p>{desc}</p>
              </div>
              {i < FEATURES.length - 1 && <span className={styles.stepArrow} aria-hidden="true"><ArrowRight size={16} /></span>}
            </Reveal>
          ))}
        </div>
      </section>

      {/* ── Product preview ── */}
      <section className={styles.preview} id="preview">
        <div className={styles.sectionHeader}>
          <p className={styles.sectionEyebrow}>See it in action</p>
          <h2>One dashboard, every string accounted for.</h2>
        </div>
        <Reveal>
          <ProductPreview />
        </Reveal>
      </section>

      {/* ── Tech strip ── */}
      <section className={styles.techStrip} aria-label="Built with">
        <span className={styles.techLabel}>Built on</span>
        <div className={styles.techList}>
          {TECH.map(t => <span key={t} className={styles.techBadge}>{t}</span>)}
        </div>
      </section>

      {/* ── About ── */}
      <section className={styles.about} id="about">
        <div className={styles.aboutGrid}>
          <Reveal>
            <div className={styles.aboutText}>
              <p className={styles.sectionEyebrow}>About OpenSunray</p>
              <h2>Built alongside the people who walk the rows.</h2>
              <p>
                OpenSunray Insight grew out of field work on real plants. Every prediction is
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
                <span className={styles.missionNote}>why OpenSunray exists</span>
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

      {/* ── CTA band ── */}
      <section className={styles.cta}>
        <Reveal>
          <div className={styles.ctaInner}>
            <div>
              <p className={styles.sectionEyebrow} style={{ borderColor: 'rgba(255,255,255,0.25)', color: 'rgba(255,255,255,0.75)' }}>
                <EyeOff size={13} style={{ verticalAlign: '-2px', marginRight: '0.4rem' }} />
                Ready when you are
              </p>
              <h2 className={styles.ctaTitle}>See what your array has been hiding.</h2>
            </div>
            <div className={styles.heroCtas}>
              <Link href="/auth" className="btn btn-lg" style={{ background: '#fff', color: 'var(--color-primary)' }}>
                Enter Dashboard <ChevronRight size={18} />
              </Link>
              <a
                href="https://www.linkedin.com/company/opensunray"
                target="_blank" rel="noreferrer"
                className="btn btn-outline btn-lg"
                style={{ borderColor: 'rgba(255,255,255,0.5)', color: '#fff' }}
              >
                Talk to the team
              </a>
            </div>
          </div>
        </Reveal>
      </section>

      {/* ── Footer ── */}
      <footer className={styles.footer}>
        <div className={styles.footerGrid}>
          <div className={styles.footerBrand}>
            <Logo fontSize="1.05rem" />
            <p>AI-driven fault detection, localisation, severity analysis and rectification for solar PV arrays.</p>
          </div>
          <div className={styles.footerCol}>
            <span className={styles.footerHead}>Product</span>
            <a href="#features">How it works</a>
            <a href="#preview">Product preview</a>
            <Link href="/auth">Operator log in</Link>
          </div>
          <div className={styles.footerCol}>
            <span className={styles.footerHead}>Company</span>
            <a href="#about">About</a>
            <a href="https://www.linkedin.com/company/opensunray" target="_blank" rel="noreferrer"><ExternalLink size={13} /> LinkedIn</a>
            <a href="mailto:hello@opensunray.dev"><Mail size={13} /> hello@opensunray.dev</a>
          </div>
        </div>
        <div className={styles.footerBar}>
          <span>An OpenSunray product</span>
          <span className={styles.footerDot}>&middot;</span>
          <span>&copy; {new Date().getFullYear()}</span>
        </div>
      </footer>

      <LandingAssistant />
    </div>
  );
}
