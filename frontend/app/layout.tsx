import type { Metadata } from 'next';
import './globals.css';
import { AuthProvider } from '@/lib/AuthContext';
import { THEME_INIT_SCRIPT } from '@/lib/theme';
import SplashScreen from '@/components/fx/SplashScreen';
import SmoothScroll from '@/components/fx/SmoothScroll';
import CursorGlow from '@/components/fx/CursorGlow';

export const metadata: Metadata = {
  title: 'OpenSunray Insight — Solar Intelligence Hub',
  description: 'AI-powered solar panel fault detection, localisation, severity analysis, and rectification. An OpenSunray product.',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <head>
        {/* App Router loads these globally; the no-page-custom-font rule is a pages-dir legacy warning. */}
        {/* eslint-disable-next-line @next/next/no-page-custom-font */}
        <link
          href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap"
          rel="stylesheet"
        />
        <script dangerouslySetInnerHTML={{ __html: THEME_INIT_SCRIPT }} />
      </head>
      <body>
        <AuthProvider>
          <SmoothScroll />
          <SplashScreen />
          {children}
          <CursorGlow />
        </AuthProvider>
      </body>
    </html>
  );
}
