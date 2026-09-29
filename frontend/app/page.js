'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/hooks/useAuth';

export default function RootPage() {
  const { isAuthenticated, isSuperAdmin, loading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!loading) {
      if (isAuthenticated) {
        if (isSuperAdmin) {
          router.push('/super-admin/organizations');
        } else {
          router.push('/dashboard');
        }
      } else {
        router.push('/login');
      }
    }
  }, [isAuthenticated, isSuperAdmin, loading, router]);

  if (loading) {
    return (
      <div className="min-h-screen bg-navy flex items-center justify-center">
        <div className="w-24 h-24 rounded-full border-t-2 border-brand animate-spin" />
        <div className="absolute inset-0 shimmer-bg pointer-events-none opacity-20" />
      </div>
    );
  }

  return null;
}
