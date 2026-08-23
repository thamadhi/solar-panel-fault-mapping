'use client';

import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';
import { useAuth } from '@/lib/AuthContext';
import { ROLE_PERMISSIONS } from './DashboardLayout';
import ThemeToggle from '@/components/ui/ThemeToggle';
import LogoWord from '@/components/ui/Logo';
import styles from './Sidebar.module.css';
import {
  LayoutDashboard, Zap, MapPin, AlertTriangle, Wrench,
  History, Settings, HelpCircle, LogOut,
} from 'lucide-react';

const NAV_ITEMS = [
  { key: 'Dashboard',       label: 'Dashboard',       href: '/dashboard',              icon: LayoutDashboard },
  { key: 'Fault Detection', label: 'Fault Detection',  href: '/dashboard/detection',    icon: Zap },
  { key: 'Localisation',    label: 'Localisation',     href: '/dashboard/localisation', icon: MapPin },
  { key: 'Severity',        label: 'Severity',         href: '/dashboard/severity',     icon: AlertTriangle },
  { key: 'Rectification',   label: 'Rectification',    href: '/dashboard/rectification',icon: Wrench },
  { key: 'History',         label: 'Activity Log',     href: '/dashboard/history',      icon: History },
  { key: 'PV System Config',label: 'System Config',    href: '/dashboard/config',       icon: Settings },
];

const HELP_ITEM = { key: 'Help', label: 'Support Center', href: '/dashboard/help', icon: HelpCircle };

export default function Sidebar() {
  const { user, logout } = useAuth();
  const pathname = usePathname();
  const router   = useRouter();

  const userType    = user?.type || 'Standard';
  const allowed     = ROLE_PERMISSIONS[userType] ?? ROLE_PERMISSIONS.Standard;
  const filteredNav = NAV_ITEMS.filter(item => allowed.includes(item.key));

  function handleLogout() {
    logout();
    router.replace('/');
  }

  return (
    <aside className={styles.sidebar}>
      {/* Brand */}
      <div className={styles.brand}>
        <div>
          <LogoWord fontSize="1.05rem" />
          <div className={styles.brandSub}>Solar Intelligence Hub</div>
        </div>
      </div>

      <hr style={{ borderColor: 'var(--color-border)', margin: '0.75rem 0' }} />

      {/* User info */}
      {user && (
        <div className={styles.userBox}>
          <div className={styles.userLabel}>Operator</div>
          <div className={styles.userName}>{user.username}</div>
          <div className={styles.userRole}>{user.type} Mode</div>
        </div>
      )}

      {/* Nav */}
      <div className={styles.navLabel}>Main Menu</div>
      <nav className={styles.nav}>
        {filteredNav.map(({ key, label, href, icon: Icon }) => {
          const active = pathname === href || (href !== '/dashboard' && pathname.startsWith(href));
          return (
            <Link
              key={key}
              href={href}
              className={`${styles.navItem} ${active ? styles.navItemActive : ''}`}
            >
              <Icon size={16} strokeWidth={2} />
              <span>{label}</span>
            </Link>
          );
        })}
      </nav>

      <div className={styles.bottom}>
        <Link
          href={HELP_ITEM.href}
          className={`${styles.navItem} ${pathname === HELP_ITEM.href ? styles.navItemActive : ''}`}
        >
          <HelpCircle size={16} strokeWidth={2} />
          <span>{HELP_ITEM.label}</span>
        </Link>

        <div className={styles.themeRow}>
          <span className={styles.themeLabel}>{'Night mode'}</span>
          <ThemeToggle />
        </div>

        <button className={styles.logoutBtn} onClick={handleLogout}>
          <LogOut size={15} strokeWidth={2} />
          Terminate Session
        </button>
      </div>
    </aside>
  );
}
