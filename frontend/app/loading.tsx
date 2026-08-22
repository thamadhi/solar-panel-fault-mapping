export default function Loading() {
  return (
    <div className="splash">
      <div className="splashLogo">
        <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="var(--color-accent)" strokeWidth="2.2" style={{ animation: 'splashPulse 1.5s ease-in-out infinite' }}>
          <circle cx="12" cy="12" r="4" />
          <path d="M12 2v2M12 20v2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M2 12h2M20 12h2M6.34 17.66l-1.41 1.41M19.07 4.93l-1.41 1.41" strokeLinecap="round" />
        </svg>
        OpenPVisor Insight
      </div>
      <div className="splashBar" />
    </div>
  );
}
