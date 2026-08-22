export default function DashboardLoading() {
  return (
    <div className="loading-overlay" style={{ minHeight: '60vh', justifyContent: 'center' }}>
      <div className="spinner spinner-lg" />
      <span>Loading dashboard…</span>
    </div>
  );
}
