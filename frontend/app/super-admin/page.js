'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { Building2, CreditCard, Activity, ShieldAlert, Plus, ArrowRight, CheckCircle, AlertCircle } from 'lucide-react';
import { apiClient } from '@/lib/api/client';
import toast from 'react-hot-toast';

export default function SuperAdminDashboardPage() {
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState({
    totalOrgs: 0,
    activeOrgs: 0,
    suspendedOrgs: 0,
    plansCount: 0,
  });
  const [recentLogs, setRecentLogs] = useState([]);
  const [recentOrgs, setRecentOrgs] = useState([]);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    setLoading(true);
    try {
      const [orgsRes, plansRes, logsRes] = await Promise.all([
        apiClient.get('/admin/organizations?page=1&page_size=5'),
        apiClient.get('/admin/subscription-plans'),
        apiClient.get('/admin/audit-logs?page=1&page_size=5'),
      ]);

      const orgs = orgsRes.data.data || [];
      const totalOrgs = orgsRes.data.total || 0;
      const activeOrgs = orgs.filter(o => o.status === 'active' || o.status === 'trial').length;
      const suspendedOrgs = orgs.filter(o => o.status === 'suspended').length;
      const plans = plansRes.data.data || [];

      setStats({
        totalOrgs,
        activeOrgs,
        suspendedOrgs,
        plansCount: plans.length,
      });
      setRecentOrgs(orgs);
      setRecentLogs(logsRes.data.data || []);
    } catch (err) {
      toast.error('Failed to load dashboard statistics');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="p-8 flex items-center justify-center min-h-[60vh]">
        <div className="w-12 h-12 border-2 border-brand-light border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  return (
    <div className="p-8 space-y-8">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-display font-bold text-white">Platform Overview</h1>
          <p className="text-gray-400 mt-1 text-sm">Real-time status of multi-tenant jewellery store tenants</p>
        </div>
        <Link
          href="/super-admin/organizations"
          className="px-4 py-2.5 bg-gradient-gold text-white font-medium rounded-lg hover:shadow-lg hover:shadow-brand/20 transition-all flex items-center gap-2"
        >
          <Plus className="w-4 h-4" /> Add Organization
        </Link>
      </div>

      {/* Metric Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="glass-card p-6 flex items-center justify-between">
          <div>
            <p className="text-xs font-medium text-gray-400 uppercase tracking-wider">Total Stores</p>
            <h3 className="text-3xl font-bold text-white mt-1">{stats.totalOrgs}</h3>
          </div>
          <div className="w-12 h-12 rounded-xl bg-brand/10 border border-brand/20 flex items-center justify-center text-brand-light">
            <Building2 className="w-6 h-6" />
          </div>
        </div>

        <div className="glass-card p-6 flex items-center justify-between">
          <div>
            <p className="text-xs font-medium text-gray-400 uppercase tracking-wider">Active Stores</p>
            <h3 className="text-3xl font-bold text-emerald-400 mt-1">{stats.activeOrgs}</h3>
          </div>
          <div className="w-12 h-12 rounded-xl bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-emerald-400">
            <CheckCircle className="w-6 h-6" />
          </div>
        </div>

        <div className="glass-card p-6 flex items-center justify-between">
          <div>
            <p className="text-xs font-medium text-gray-400 uppercase tracking-wider">Suspended</p>
            <h3 className="text-3xl font-bold text-rose-400 mt-1">{stats.suspendedOrgs}</h3>
          </div>
          <div className="w-12 h-12 rounded-xl bg-rose-500/10 border border-rose-500/20 flex items-center justify-center text-rose-400">
            <ShieldAlert className="w-6 h-6" />
          </div>
        </div>

        <div className="glass-card p-6 flex items-center justify-between">
          <div>
            <p className="text-xs font-medium text-gray-400 uppercase tracking-wider">Subscription Plans</p>
            <h3 className="text-3xl font-bold text-amber-400 mt-1">{stats.plansCount}</h3>
          </div>
          <div className="w-12 h-12 rounded-xl bg-amber-500/10 border border-amber-500/20 flex items-center justify-center text-amber-400">
            <CreditCard className="w-6 h-6" />
          </div>
        </div>
      </div>

      {/* Grid: Recent Organizations & Audit Activity */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Recent Organizations */}
        <div className="glass-card p-6 space-y-4">
          <div className="flex justify-between items-center border-b border-white/10 pb-4">
            <h2 className="text-lg font-bold text-white flex items-center gap-2">
              <Building2 className="w-5 h-5 text-brand-light" /> Recent Organizations
            </h2>
            <Link href="/super-admin/organizations" className="text-xs text-brand-light hover:underline flex items-center gap-1">
              View All <ArrowRight className="w-3 h-3" />
            </Link>
          </div>

          <div className="space-y-3">
            {recentOrgs.length === 0 ? (
              <p className="text-sm text-gray-400 py-4 text-center">No organizations onboarded yet.</p>
            ) : (
              recentOrgs.map((org) => (
                <div key={org.id} className="p-3.5 rounded-lg bg-white/5 hover:bg-white/10 transition-colors flex items-center justify-between">
                  <div>
                    <Link href={`/super-admin/organizations/${org.id}`} className="font-semibold text-white hover:text-brand-light">
                      {org.name}
                    </Link>
                    <p className="text-xs text-gray-400 mt-0.5">Slug: {org.slug} • {org.currency}</p>
                  </div>
                  <span className={`px-2.5 py-1 rounded-full text-xs font-medium border ${
                    org.status === 'active' ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20' : 'bg-rose-500/10 text-rose-400 border-rose-500/20'
                  }`}>
                    {org.status}
                  </span>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Audit Trail Log */}
        <div className="glass-card p-6 space-y-4">
          <div className="flex justify-between items-center border-b border-white/10 pb-4">
            <h2 className="text-lg font-bold text-white flex items-center gap-2">
              <Activity className="w-5 h-5 text-amber-400" /> Administrative Audit Activity
            </h2>
            <Link href="/super-admin/audit-logs" className="text-xs text-brand-light hover:underline flex items-center gap-1">
              View All <ArrowRight className="w-3 h-3" />
            </Link>
          </div>

          <div className="space-y-3">
            {recentLogs.length === 0 ? (
              <p className="text-sm text-gray-400 py-4 text-center">No audit logs recorded yet.</p>
            ) : (
              recentLogs.map((log) => (
                <div key={log.id} className="p-3.5 rounded-lg bg-white/5 flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-white">{log.action}</p>
                    <p className="text-xs text-gray-400 mt-0.5">{new Date(log.created_at).toLocaleString()}</p>
                  </div>
                  <span className="text-xs text-gray-400 font-mono bg-black/30 px-2 py-1 rounded">
                    {log.entity_type || 'system'}
                  </span>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
