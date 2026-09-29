'use client';

import { useState, useEffect } from 'react';
import { CreditCard, Plus, Check, Edit2, Shield, Layers } from 'lucide-react';
import { apiClient } from '@/lib/api/client';
import toast from 'react-hot-toast';

export default function SubscriptionPlansPage() {
  const [plans, setPlans] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);

  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [priceMonthly, setPriceMonthly] = useState('0');
  const [featuresInput, setFeaturesInput] = useState('inventory.view, inventory.create, sales.create, customers.view');
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    fetchPlans();
  }, []);

  const fetchPlans = async () => {
    setLoading(true);
    try {
      const res = await apiClient.get('/admin/subscription-plans');
      setPlans(res.data.data || []);
    } catch (err) {
      toast.error('Failed to load subscription plans');
    } finally {
      setLoading(false);
    }
  };

  const handleCreatePlan = async (e) => {
    e.preventDefault();
    setSaving(true);
    try {
      const featureKeys = featuresInput.split(',').map(s => s.trim()).filter(Boolean);
      const features = featureKeys.map(k => ({
        feature_key: k,
        enabled: true,
      }));

      await apiClient.post('/admin/subscription-plans', {
        name,
        description,
        price_monthly: parseFloat(priceMonthly) || 0,
        currency: 'INR',
        status: 'active',
        features,
      });

      toast.success('Subscription plan created successfully');
      setShowModal(false);
      setName('');
      setDescription('');
      fetchPlans();
    } catch (err) {
      toast.error(err.response?.data?.message || 'Failed to create plan');
    } finally {
      setSaving(false);
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
    <div className="p-8 space-y-8 max-w-7xl mx-auto">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-display font-bold text-white flex items-center gap-3">
            <CreditCard className="w-8 h-8 text-amber-400" /> Subscription Plans
          </h1>
          <p className="text-gray-400 mt-1 text-sm">Configure multi-tenant subscription tiers and default feature entitlements</p>
        </div>
        <button
          onClick={() => setShowModal(true)}
          className="px-4 py-2.5 bg-gradient-gold text-white font-medium rounded-lg hover:shadow-lg transition-all flex items-center gap-2"
        >
          <Plus className="w-4 h-4" /> Create New Plan
        </button>
      </div>

      {/* Plan Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {plans.map((plan) => (
          <div key={plan.id} className="glass-card p-6 flex flex-col justify-between space-y-6 border border-white/10 hover:border-brand/30 transition-all">
            <div className="space-y-4">
              <div className="flex justify-between items-start">
                <div>
                  <h3 className="text-xl font-bold text-white">{plan.name}</h3>
                  <p className="text-xs text-gray-400 mt-1 line-clamp-2">{plan.description || 'Standard subscription tier'}</p>
                </div>
                <span className="px-2.5 py-1 rounded-full text-xs font-medium bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 uppercase">
                  {plan.status}
                </span>
              </div>

              <div className="py-2">
                <span className="text-3xl font-bold text-gradient-gold">₹{plan.price_monthly || 0}</span>
                <span className="text-xs text-gray-400"> / month</span>
              </div>

              {/* Feature list */}
              <div className="space-y-2 pt-2 border-t border-white/10">
                <p className="text-xs font-medium uppercase text-gray-400 tracking-wider">Enabled Feature Keys:</p>
                <div className="space-y-1.5 max-h-40 overflow-y-auto pr-2">
                  {plan.features?.length === 0 ? (
                    <p className="text-xs text-gray-500 italic">No feature entitlements set.</p>
                  ) : (
                    plan.features?.map((f) => (
                      <div key={f.id} className="flex items-center gap-2 text-xs text-gray-300">
                        <Check className="w-3.5 h-3.5 text-emerald-400 flex-shrink-0" />
                        <span className="font-mono">{f.feature_key}</span>
                      </div>
                    ))
                  )}
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Create Plan Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="glass-card w-full max-w-lg p-6 space-y-6">
            <h2 className="text-xl font-bold text-white">Create Subscription Plan</h2>

            <form onSubmit={handleCreatePlan} className="space-y-4">
              <div>
                <label className="text-sm font-medium text-gray-300">Plan Name</label>
                <input
                  type="text"
                  placeholder="e.g. ENTERPRISE"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  className="glass-input w-full px-4 py-2.5 mt-1"
                  required
                />
              </div>

              <div>
                <label className="text-sm font-medium text-gray-300">Description</label>
                <textarea
                  placeholder="Plan description..."
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  className="glass-input w-full px-4 py-2 mt-1 text-sm h-20"
                />
              </div>

              <div>
                <label className="text-sm font-medium text-gray-300">Monthly Price (INR)</label>
                <input
                  type="number"
                  placeholder="9999"
                  value={priceMonthly}
                  onChange={(e) => setPriceMonthly(e.target.value)}
                  className="glass-input w-full px-4 py-2.5 mt-1"
                  required
                />
              </div>

              <div>
                <label className="text-sm font-medium text-gray-300">Feature Keys (Comma separated)</label>
                <input
                  type="text"
                  value={featuresInput}
                  onChange={(e) => setFeaturesInput(e.target.value)}
                  className="glass-input w-full px-4 py-2.5 mt-1 font-mono text-xs"
                  required
                />
              </div>

              <div className="flex gap-3 pt-4 border-t border-white/10">
                <button
                  type="button"
                  onClick={() => setShowModal(false)}
                  className="flex-1 py-2.5 bg-white/5 hover:bg-white/10 text-gray-300 rounded-lg font-medium text-sm"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={saving}
                  className="flex-1 py-2.5 bg-gradient-gold text-white rounded-lg font-medium text-sm shadow-lg shadow-brand/20"
                >
                  {saving ? 'Creating...' : 'Save Subscription Plan'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
