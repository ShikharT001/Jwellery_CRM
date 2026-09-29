'use client';

import { useAuth } from '@/hooks/useAuth';
import { DollarSign, Package, Users, ShoppingBag, Plus } from 'lucide-react';
import Button from '@/components/ui/Button';

export default function DashboardPage() {
  const { user } = useAuth();

  const stats = [
    { label: 'Total Sales', value: '$24,500', trend: '+12.5%', icon: DollarSign, color: 'text-green-400' },
    { label: 'Active Inventory', value: '1,248', trend: '+3.2%', icon: Package, color: 'text-brand-light' },
    { label: 'Total Customers', value: '842', trend: '+8.1%', icon: Users, color: 'text-blue-400' },
    { label: 'Pending Orders', value: '14', trend: '-2.4%', icon: ShoppingBag, color: 'text-yellow-400' },
  ];

  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-display font-bold text-white">
            Welcome back, <span className="text-gradient-gold">{user?.display_name || 'Admin'}</span>
          </h1>
          <p className="text-gray-400 mt-1">Here's what's happening with your store today.</p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map((stat, i) => {
          const Icon = stat.icon;
          const isPositive = stat.trend.startsWith('+');
          
          return (
            <div key={i} className="glass-card p-6 animate-slide-up" style={{ animationDelay: `${i * 100}ms` }}>
              <div className="flex justify-between items-start mb-4">
                <div className={`p-3 rounded-xl bg-white/5 ${stat.color}`}>
                  <Icon className="w-6 h-6" />
                </div>
                <span className={`text-sm font-medium ${isPositive ? 'text-green-400' : 'text-red-400'}`}>
                  {stat.trend}
                </span>
              </div>
              <p className="text-gray-400 text-sm font-medium mb-1">{stat.label}</p>
              <h3 className="text-2xl font-display font-bold text-white">{stat.value}</h3>
            </div>
          );
        })}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-2 glass-card p-6 min-h-[400px]">
          <h2 className="text-xl font-display font-semibold text-white mb-6">Recent Activity</h2>
          <div className="flex flex-col items-center justify-center h-64 text-gray-500">
            <div className="w-16 h-16 rounded-full bg-white/5 flex items-center justify-center mb-4">
              <span className="text-2xl">📈</span>
            </div>
            <p>Activity chart will appear here</p>
          </div>
        </div>
        
        <div className="glass-card p-6">
          <h2 className="text-xl font-display font-semibold text-white mb-6">Quick Actions</h2>
          <div className="space-y-3">
            <Button variant="secondary" className="w-full justify-start" icon={Plus}>New Sale</Button>
            <Button variant="secondary" className="w-full justify-start" icon={Plus}>Add Inventory</Button>
            <Button variant="secondary" className="w-full justify-start" icon={Plus}>New Customer</Button>
            <Button variant="secondary" className="w-full justify-start" icon={Plus}>New Purchase</Button>
          </div>
        </div>
      </div>
    </div>
  );
}
