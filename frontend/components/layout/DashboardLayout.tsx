'use client';

import { useEffect } from 'react';
import { useRouter, usePathname } from 'next/navigation';
import Logo from '@/components/ui/Logo';
import { useAuth } from '@/lib/AuthContext';
import Sidebar from './Sidebar';
import styles from './DashboardLayout.module.css';

const ROLE_PERMISSIONS: Record<string, string[]> = {
  Technician:       ['Dashboard', 'Fault Detection', 'Localisation', 'Rectification', 'History', 'PV System Config'],
  Admin:            ['Dashboard', 'Fault Detection', 'Localisation', 'Rectification', 'Severity', 'History', 'PV System Config'],
  'Solar PV Operator': ['Dashboard', 'Fault Detection', 'Localisation', 'Severity', 'History', 'PV System Config'],
  Standard:         ['Dashboard'],
};

export { ROLE_PERMISSIONS };

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const { isAuthenticated } = useAuth();
  const router = useRouter();
  const pathname = usePathname();

  useEffect(() => {
    if (!isAuthenticated) router.replace('/auth');
  }, [isAuthenticated, router]);

  // Branded boot screen instead of a blank flash while auth state rehydrates
  if (!isAuthenticated) {
    return (
      <div className="splash">
        <div className="splashLogo">
          <Logo fontSize="clamp(1.15rem, 4vw, 1.6rem)" />
        </div>
        <div className="splashBar" />
        <div className="splashText">Restoring session…</div>
      </div>
    );
  }

  return (
    <div className={styles.layout}>
      <Sidebar />
      <main className={styles.main}>
        {/* key remounts per route so the page-enter animation plays on navigation */}
        <div key={pathname} className={`${styles.content} page-enter`}>
          {children}
        </div>
      </main>
    </div>
  );
}
