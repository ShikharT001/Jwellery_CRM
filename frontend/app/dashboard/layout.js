'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/hooks/useAuth';
import Sidebar from '@/components/layout/Sidebar';

export default function DashboardLayout({ children }) {
  const { isAuthenticated, loading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!loading && !isAuthenticated) {
      router.push('/login');
    }
  }, [loading, isAuthenticated, router]);

  if (loading || !isAuthenticated) {
    return (
      <div className="min-h-screen bg-navy flex items-center justify-center">
        <div className="w-16 h-16 rounded-full border-t-2 border-brand animate-spin" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-navy flex">
      <Sidebar />
      <main className="flex-1 ml-[280px] p-8 animate-fade-in">
        {children}
      </main>
    </div>
  );
}
