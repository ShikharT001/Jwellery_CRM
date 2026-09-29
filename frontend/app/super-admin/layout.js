'use client';

import { useEffect } from 'react';
import { useRouter, usePathname } from 'next/navigation';
import { useAuth } from '@/hooks/useAuth';
import Link from 'next/link';
import { Building2, CreditCard, Activity, Settings, LogOut, ArrowLeft, LayoutDashboard } from 'lucide-react';

export default function SuperAdminLayout({ children }) {
  const { isAuthenticated, isSuperAdmin, loading, user, logout } = useAuth();
  const router = useRouter();
  const pathname = usePathname();

  useEffect(() => {
    if (!loading) {
      if (!isAuthenticated) {
        router.push('/login');
      } else if (!isSuperAdmin) {
        router.push('/dashboard');
      }
    }
  }, [loading, isAuthenticated, isSuperAdmin, router]);

  if (loading || !isAuthenticated || !isSuperAdmin) {
    return (
      <div className="min-h-screen bg-navy flex items-center justify-center">
        <div className="w-16 h-16 rounded-full border-t-2 border-brand animate-spin" />
      </div>
    );
  }

  const navItems = [
    { name: 'Dashboard', href: '/super-admin', icon: LayoutDashboard },
    { name: 'Organizations', href: '/super-admin/organizations', icon: Building2 },
    { name: 'Subscription Plans', href: '/super-admin/subscription-plans', icon: CreditCard },
    { name: 'Audit Logs', href: '/super-admin/audit-logs', icon: Activity },
  ];

  return (
    <div className="min-h-screen bg-navy flex">
      {/* Super Admin Sidebar */}
      <div className="w-[280px] h-screen fixed left-0 top-0 glass-card border-l-0 border-y-0 rounded-none flex flex-col z-40 bg-navy/90">
        <div className="p-6 border-b border-white/10">
          <h2 className="text-xl font-display font-bold text-gradient-gold flex items-center gap-2">
            <span>⚡</span> Super Admin Portal
          </h2>
        </div>

        <div className="flex-1 overflow-y-auto px-4 py-4 space-y-1">
          {navItems.map((item) => {
            const isActive = item.href === '/super-admin'
              ? pathname === '/super-admin'
              : pathname === item.href || pathname.startsWith(`${item.href}/`);
            const Icon = item.icon;
            
            return (
              <Link
                key={item.name}
                href={item.href}
                className={`
                  flex items-center gap-3 px-3 py-2.5 rounded-lg transition-all text-sm font-medium
                  ${isActive 
                    ? 'bg-brand/20 text-brand-light border-l-2 border-brand' 
                    : 'text-gray-400 hover:text-white hover:bg-white/5 border-l-2 border-transparent'
                  }
                `}
              >
                <Icon className={`w-5 h-5 ${isActive ? 'text-brand-light' : 'text-gray-400'}`} />
                {item.name}
              </Link>
            );
          })}
        </div>

        <div className="p-4 border-t border-white/10 mt-auto space-y-2">
          <Link 
            href="/dashboard"
            className="w-full flex items-center justify-center gap-2 py-2 text-sm text-brand-light hover:bg-brand/10 rounded-lg transition-colors"
          >
            <ArrowLeft className="w-4 h-4" />
            Back to Dashboard
          </Link>
          <button
            onClick={logout}
            className="w-full flex items-center justify-center gap-2 py-2 text-sm text-gray-400 hover:text-white hover:bg-white/5 rounded-lg transition-colors"
          >
            <LogOut className="w-4 h-4" />
            Sign Out
          </button>
        </div>
      </div>

      {/* Main Content */}
      <main className="flex-1 ml-[280px]">
        {/* Top Header */}
        <header className="h-16 glass-card border-x-0 border-t-0 rounded-none flex items-center justify-between px-8 sticky top-0 z-30">
          <div></div>
          <div className="flex items-center gap-3">
            <span className="px-2.5 py-1 rounded-full bg-brand/20 text-brand-light text-xs font-medium border border-brand/30 flex items-center gap-1.5">
              <span className="w-1.5 h-1.5 rounded-full bg-brand-light animate-pulse" />
              Super Admin
            </span>
            <span className="text-sm font-medium text-white">{user?.display_name}</span>
          </div>
        </header>
        
        <div className="p-8 animate-fade-in">
          {children}
        </div>
      </main>
    </div>
  );
}
