import DashboardLayout from '@/components/layout/DashboardLayout';
import AssistantWidget from '@/components/chat/AssistantWidget';

export default function Layout({ children }: { children: React.ReactNode }) {
  return (
    <DashboardLayout>
      {children}
      <AssistantWidget />
    </DashboardLayout>
  );
}
