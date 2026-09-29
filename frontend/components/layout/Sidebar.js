'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useAuth } from '@/hooks/useAuth';
import { 
  Gem, 
  LayoutDashboard, 
  Package, 
  ShoppingCart, 
  Users, 
  TrendingUp, 
  Hammer, 
  PieChart, 
  Settings,
  LogOut,
  ShieldAlert
} from 'lucide-react';

const navItems = [
  { name: 'Dashboard', href: '/dashboard', icon: LayoutDashboard },
  { name: 'Inventory', href: '/dashboard/inventory', icon: Package },
  { name: 'Sales', href: '/dashboard/sales', icon: ShoppingCart },
  { name: 'Customers', href: '/dashboard/customers', icon: Users },
  { name: 'Purchases', href: '/dashboard/purchases', icon: TrendingUp },
  { name: 'Manufacturing', href: '/dashboard/manufacturing', icon: Hammer },
  { name: 'Reports', href: '/dashboard/reports', icon: PieChart },
  { name: 'Settings', href: '/dashboard/settings', icon: Settings },
];

export default function Sidebar({ items = navItems }) {
  const pathname = usePathname();
  const { user, logout, isSuperAdmin } = useAuth();

  return (
    <div className="w-[280px] h-screen fixed left-0 top-0 glass-card border-l-0 border-y-0 rounded-none flex flex-col z-40 bg-navy/80">
      <div className="p-6 flex items-center gap-3">
        <div className="w-10 h-10 rounded-xl bg-white/5 border border-brand/30 flex items-center justify-center relative overflow-hidden group">
          <div className="absolute inset-0 bg-brand/20 opacity-0 group-hover:opacity-100 transition-opacity" />
          <Gem className="w-6 h-6 text-brand-light relative z-10" />
        </div>
        <span className="text-xl font-display font-bold text-gradient-gold tracking-wide">JewelERP</span>
      </div>

      <div className="flex-1 overflow-y-auto px-4 py-2 space-y-1">
        {isSuperAdmin && !pathname.startsWith('/super-admin') && (
          <div className="mb-4">
            <Link 
              href="/super-admin"
              className="flex items-center gap-3 px-3 py-2.5 rounded-lg text-brand-light hover:bg-brand/10 transition-colors font-medium text-sm"
            >
              <ShieldAlert className="w-5 h-5" />
              Admin Portal
            </Link>
            <div className="h-px bg-white/10 my-3 mx-2" />
          </div>
        )}

        {items.map((item) => {
          const isActive = pathname === item.href || pathname.startsWith(`${item.href}/`);
          const Icon = item.icon;
          
          return (
            <Link
              key={item.name}
              href={item.href}
              className={`
                flex items-center gap-3 px-3 py-2.5 rounded-lg transition-all text-sm font-medium
                ${isActive 
                  ? 'bg-brand/10 text-white border-l-2 border-brand' 
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

      <div className="p-4 border-t border-white/10 mt-auto">
        <div className="flex items-center gap-3 p-3 rounded-lg bg-white/5 mb-3">
          <div className="w-8 h-8 rounded-full bg-gradient-gold flex items-center justify-center text-white font-bold font-display text-sm">
            {user?.display_name?.charAt(0)?.toUpperCase() || 'U'}
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium text-white truncate">{user?.display_name}</p>
            <p className="text-xs text-gray-400 truncate">{user?.email}</p>
          </div>
        </div>
        <button
          onClick={logout}
          className="w-full flex items-center justify-center gap-2 py-2 text-sm text-gray-400 hover:text-white hover:bg-white/5 rounded-lg transition-colors"
        >
          <LogOut className="w-4 h-4" />
          Sign Out
        </button>
      </div>
    </div>
  );
}
