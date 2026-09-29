'use client';

import { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { Building2, CreditCard, Shield, ArrowLeft, Check, AlertTriangle, Plus, ToggleLeft, ToggleRight } from 'lucide-react';
import { apiClient } from '@/lib/api/client';
import toast from 'react-hot-toast';

export default function OrganizationDetailPage() {
  const { id } = useParams();
  const router = useRouter();

  const [org, setOrg] = useState(null);
  const [subscription, setSubscription] = useState(null);
  const [overrides, setOverrides] = useState([]);
  const [plans, setPlans] = useState([]);
  const [loading, setLoading] = useState(true);

  const [selectedPlanId, setSelectedPlanId] = useState('');
  const [overrideKey, setOverrideKey] = useState('');
  const [overrideEnabled, setOverrideEnabled] = useState(true);
  const [overrideReason, setOverrideReason] = useState('');
  const [savingSub, setSavingSub] = useState(false);
  const [savingOverride, setSavingOverride] = useState(false);

  useEffect(() => {
    fetchData();
  }, [id]);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [orgRes, subRes, overridesRes, plansRes] = await Promise.all([
        apiClient.get(`/organizations/${id}`),
        apiClient.get(`/admin/organizations/${id}/subscription`),
        apiClient.get(`/admin/organizations/${id}/feature-overrides`),
        apiClient.get('/admin/subscription-plans'),
      ]);

      setOrg(orgRes.data.data);
      setSubscription(subRes.data.data);
      setOverrides(overridesRes.data.data || []);
      setPlans(plansRes.data.data || []);
      if (subRes.data.data?.plan_id) {
        setSelectedPlanId(subRes.data.data.plan_id);
      }
    } catch (err) {
      toast.error('Failed to load organization details');
    } finally {
      setLoading(false);
    }
  };

  const handleAssignPlan = async (e) => {
    e.preventDefault();
    if (!selectedPlanId) return;
    setSavingSub(true);
    try {
      const res = await apiClient.post(`/admin/organizations/${id}/subscription`, {
        plan_id: selectedPlanId,
      });
      setSubscription(res.data.data);
      toast.success('Subscription plan assigned successfully');
    } catch (err) {
      toast.error(err.response?.data?.message || 'Failed to assign plan');
    } finally {
      setSavingSub(false);
    }
  };

  const handleSaveOverride = async (e) => {
    e.preventDefault();
    if (!overrideKey) return;
    setSavingOverride(true);
    try {
      await apiClient.post(`/admin/organizations/${id}/feature-overrides`, {
        feature_key: overrideKey,
        enabled: overrideEnabled,
        reason: overrideReason,
      });
      toast.success('Feature override updated');
      setOverrideKey('');
      setOverrideReason('');
      fetchData();
    } catch (err) {
      toast.error(err.response?.data?.message || 'Failed to update feature override');
    } finally {
      setSavingOverride(false);
    }
  };

  const handleToggleStatus = async () => {
    const newStatus = org.status === 'suspended' ? 'active' : 'suspended';
    const reason = prompt(`Enter reason for changing status to '${newStatus}':`) || 'Administrative status update';
    try {
      const res = await apiClient.patch(`/organizations/${id}/status`, {
        status: newStatus,
        reason,
      });
      setOrg(res.data.data);
      toast.success(`Organization status changed to ${newStatus}`);
    } catch (err) {
      toast.error(err.response?.data?.message || 'Failed to change status');
    }
  };

  if (loading || !org) {
    return (
      <div className="p-8 flex items-center justify-center min-h-[60vh]">
        <div className="w-12 h-12 border-2 border-brand-light border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  return (
    <div className="p-8 space-y-8 max-w-6xl mx-auto">
      {/* Back Header */}
      <div className="flex items-center gap-4">
        <button
          onClick={() => router.push('/super-admin/organizations')}
          className="p-2 rounded-lg bg-white/5 hover:bg-white/10 text-gray-300 transition-colors"
        >
          <ArrowLeft className="w-5 h-5" />
        </button>
        <div>
          <h1 className="text-3xl font-display font-bold text-white flex items-center gap-3">
            {org.name}
            <span className={`text-xs px-3 py-1 rounded-full font-sans font-medium border ${
              org.status === 'active' ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20' : 'bg-rose-500/10 text-rose-400 border-rose-500/20'
            }`}>
              {org.status}
            </span>
          </h1>
          <p className="text-gray-400 text-sm mt-0.5">Slug: {org.slug} • Currency: {org.currency} • Country: {org.country}</p>
        </div>
      </div>

      {/* Action Toolbar */}
      <div className="glass-card p-4 flex justify-between items-center">
        <div>
          <span className="text-sm font-medium text-gray-300">Status Action: </span>
          <span className="text-xs text-gray-400 ml-1">Change organization state across platform</span>
        </div>
        <button
          onClick={handleToggleStatus}
          className={`px-4 py-2 rounded-lg font-medium text-sm transition-all ${
            org.status === 'suspended'
              ? 'bg-emerald-500 text-white hover:bg-emerald-600 shadow-lg shadow-emerald-500/20'
              : 'bg-rose-500 text-white hover:bg-rose-600 shadow-lg shadow-rose-500/20'
          }`}
        >
          {org.status === 'suspended' ? 'Activate Organization' : 'Suspend Organization'}
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Subscription Assignment Card */}
        <div className="glass-card p-6 space-y-6">
          <div className="border-b border-white/10 pb-4">
            <h2 className="text-lg font-bold text-white flex items-center gap-2">
              <CreditCard className="w-5 h-5 text-amber-400" /> Active Subscription Plan
            </h2>
            <p className="text-xs text-gray-400 mt-1">Assign or change the organization's platform plan tier</p>
          </div>

          <form onSubmit={handleAssignPlan} className="space-y-4">
            <div>
              <label className="text-sm font-medium text-gray-300">Select Plan</label>
              <select
                value={selectedPlanId}
                onChange={(e) => setSelectedPlanId(e.target.value)}
                className="glass-input w-full px-4 py-2.5 mt-1 text-white bg-navy"
                required
              >
                <option value="">-- Choose Plan --</option>
                {plans.map((p) => (
                  <option key={p.id} value={p.id}>
                    {p.name} (₹{p.price_monthly}/mo)
                  </option>
                ))}
              </select>
            </div>

            <button
              type="submit"
              disabled={savingSub}
              className="w-full py-2.5 bg-gradient-gold text-white font-medium rounded-lg hover:shadow-lg transition-all"
            >
              {savingSub ? 'Assigning...' : 'Assign Subscription Plan'}
            </button>
          </form>

          {subscription && (
            <div className="p-4 rounded-lg bg-white/5 border border-white/10 space-y-2">
              <div className="flex justify-between text-sm">
                <span className="text-gray-400">Current Active Plan:</span>
                <span className="font-bold text-amber-400">{subscription.plan?.name || 'Assigned'}</span>
              </div>
              <div className="flex justify-between text-xs text-gray-400">
                <span>Starts At:</span>
                <span>{new Date(subscription.starts_at).toLocaleDateString()}</span>
              </div>
            </div>
          )}
        </div>

        {/* Feature Overrides Card */}
        <div className="glass-card p-6 space-y-6">
          <div className="border-b border-white/10 pb-4">
            <h2 className="text-lg font-bold text-white flex items-center gap-2">
              <Shield className="w-5 h-5 text-brand-light" /> Feature Overrides
            </h2>
            <p className="text-xs text-gray-400 mt-1">Super Admin per-tenant feature toggles (precedes plan entitlements)</p>
          </div>

          <form onSubmit={handleSaveOverride} className="space-y-4">
            <div>
              <label className="text-sm font-medium text-gray-300">Feature Key</label>
              <input
                type="text"
                placeholder="e.g. manufacturing.view"
                value={overrideKey}
                onChange={(e) => setOverrideKey(e.target.value)}
                className="glass-input w-full px-4 py-2 mt-1"
                required
              />
            </div>

            <div className="flex items-center gap-4">
              <label className="text-sm font-medium text-gray-300">State:</label>
              <button
                type="button"
                onClick={() => setOverrideEnabled(!overrideEnabled)}
                className={`flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-semibold ${
                  overrideEnabled ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30' : 'bg-rose-500/20 text-rose-400 border border-rose-500/30'
                }`}
              >
                {overrideEnabled ? <ToggleRight className="w-4 h-4" /> : <ToggleLeft className="w-4 h-4" />}
                {overrideEnabled ? 'Enabled' : 'Disabled'}
              </button>
            </div>

            <div>
              <label className="text-sm font-medium text-gray-300">Reason</label>
              <input
                type="text"
                placeholder="Audit explanation for override"
                value={overrideReason}
                onChange={(e) => setOverrideReason(e.target.value)}
                className="glass-input w-full px-4 py-2 mt-1 text-sm"
              />
            </div>

            <button
              type="submit"
              disabled={savingOverride}
              className="w-full py-2 bg-white/10 text-white font-medium text-sm rounded-lg hover:bg-white/20 transition-all"
            >
              {savingOverride ? 'Saving...' : 'Save Feature Override'}
            </button>
          </form>

          {/* Overrides Table */}
          <div className="space-y-2 pt-2">
            <h4 className="text-xs uppercase font-semibold text-gray-400">Active Overrides</h4>
            {overrides.length === 0 ? (
              <p className="text-xs text-gray-400 italic">No per-tenant feature overrides set.</p>
            ) : (
              overrides.map((ov) => (
                <div key={ov.id} className="p-3 rounded-lg bg-white/5 flex items-center justify-between text-xs">
                  <div>
                    <span className="font-mono font-medium text-brand-light">{ov.feature_key}</span>
                    {ov.reason && <p className="text-gray-400 text-[11px] mt-0.5">{ov.reason}</p>}
                  </div>
                  <span className={`px-2 py-0.5 rounded font-semibold ${
                    ov.enabled ? 'bg-emerald-500/20 text-emerald-400' : 'bg-rose-500/20 text-rose-400'
                  }`}>
                    {ov.enabled ? 'Enabled' : 'Disabled'}
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
