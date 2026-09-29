'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { Search, Plus, Filter, Building2, Eye, ShieldAlert, CheckCircle } from 'lucide-react';
import { apiClient } from '@/lib/api/client';
import toast from 'react-hot-toast';

export const dynamic = 'force-dynamic';

export default function OrganizationsPage() {
  const [orgs, setOrgs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [showCreateModal, setShowCreateModal] = useState(false);

  // Form states
  const [name, setName] = useState('');
  const [slug, setSlug] = useState('');
  const [legalName, setLegalName] = useState('');
  const [email, setEmail] = useState('');
  const [phone, setPhone] = useState('');
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    fetchOrgs();
  }, [search, statusFilter]);

  const fetchOrgs = async () => {
    setLoading(true);
    try {
      let url = `/admin/organizations?page=1&page_size=50`;
      if (search) url += `&search=${encodeURIComponent(search)}`;
      if (statusFilter) url += `&status=${encodeURIComponent(statusFilter)}`;

      const res = await apiClient.get(url);
      setOrgs(res.data.data || []);
    } catch (err) {
      toast.error('Failed to load organizations list');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateOrg = async (e) => {
    e.preventDefault();
    setSaving(true);
    try {
      await apiClient.post('/admin/organizations', {
        name,
        slug: slug || name.toLowerCase().replace(/[^a-z0-9]+/g, '-'),
        legal_name: legalName,
        email,
        phone,
        country: 'India',
        currency: 'INR',
      });

      toast.success('Organization onboarded successfully');
      setShowCreateModal(false);
      setName('');
      setSlug('');
      setLegalName('');
      setEmail('');
      setPhone('');
      fetchOrgs();
    } catch (err) {
      toast.error(err.response?.data?.message || 'Failed to create organization');
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="p-8 space-y-8 max-w-7xl mx-auto">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-display font-bold text-white flex items-center gap-3">
            <Building2 className="w-8 h-8 text-brand-light" /> Tenant Organizations
          </h1>
          <p className="text-gray-400 mt-1 text-sm">Manage jewellery store tenants, onboard new stores, and monitor account status</p>
        </div>
        <button
          onClick={() => setShowCreateModal(true)}
          className="px-4 py-2.5 bg-gradient-gold text-white font-medium rounded-lg hover:shadow-lg transition-all flex items-center gap-2"
        >
          <Plus className="w-4 h-4" /> Onboard Organization
        </button>
      </div>

      {/* Filter Bar */}
      <div className="glass-card p-4 flex items-center justify-between gap-4">
        <div className="relative flex-1">
          <Search className="w-4 h-4 text-gray-400 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="Search organizations by name or slug..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="glass-input w-full pl-9 pr-4 py-2 text-sm"
          />
        </div>

        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          className="glass-input px-4 py-2 text-sm bg-navy text-white"
        >
          <option value="">All Statuses</option>
          <option value="active">Active</option>
          <option value="trial">Trial</option>
          <option value="suspended">Suspended</option>
          <option value="inactive">Inactive</option>
        </select>
      </div>

      {/* Organizations Table */}
      <div className="glass-card overflow-hidden">
        <table className="w-full text-left text-sm text-gray-300">
          <thead className="bg-white/5 text-xs uppercase font-semibold text-gray-400 border-b border-white/10">
            <tr>
              <th className="py-3.5 px-4">Organization Name</th>
              <th className="py-3.5 px-4">Slug</th>
              <th className="py-3.5 px-4">Contact</th>
              <th className="py-3.5 px-4">Status</th>
              <th className="py-3.5 px-4 text-right">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-white/5">
            {loading ? (
              <tr>
                <td colSpan={5} className="py-8 text-center text-gray-400">Loading organizations...</td>
              </tr>
            ) : orgs.length === 0 ? (
              <tr>
                <td colSpan={5} className="py-8 text-center text-gray-400">No organizations found.</td>
              </tr>
            ) : (
              orgs.map((org) => (
                <tr key={org.id} className="hover:bg-white/5 transition-colors">
                  <td className="py-3.5 px-4 font-semibold text-white">
                    {org.name}
                    {org.legal_name && <p className="text-xs text-gray-400 font-normal">{org.legal_name}</p>}
                  </td>
                  <td className="py-3.5 px-4 font-mono text-xs text-brand-light">
                    {org.slug}
                  </td>
                  <td className="py-3.5 px-4 text-xs text-gray-400">
                    {org.email || 'N/A'} {org.phone && `• ${org.phone}`}
                  </td>
                  <td className="py-3.5 px-4">
                    <span className={`px-2.5 py-1 rounded-full text-xs font-medium border ${
                      org.status === 'active' ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20' : 'bg-rose-500/10 text-rose-400 border-rose-500/20'
                    }`}>
                      {org.status}
                    </span>
                  </td>
                  <td className="py-3.5 px-4 text-right">
                    <Link
                      href={`/super-admin/organizations/${org.id}`}
                      className="px-3 py-1.5 rounded bg-brand/10 hover:bg-brand/20 text-brand-light text-xs font-medium inline-flex items-center gap-1.5 transition-colors"
                    >
                      <Eye className="w-3.5 h-3.5" /> Manage
                    </Link>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Create Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="glass-card w-full max-w-lg p-6 space-y-6">
            <h2 className="text-xl font-bold text-white">Onboard New Organization</h2>

            <form onSubmit={handleCreateOrg} className="space-y-4">
              <div>
                <label className="text-sm font-medium text-gray-300">Store Name</label>
                <input
                  type="text"
                  placeholder="e.g. Tanishq Jewellery"
                  value={name}
                  onChange={(e) => {
                    setName(e.target.value);
                    if (!slug) setSlug(e.target.value.toLowerCase().replace(/[^a-z0-9]+/g, '-'));
                  }}
                  className="glass-input w-full px-4 py-2.5 mt-1"
                  required
                />
              </div>

              <div>
                <label className="text-sm font-medium text-gray-300">Slug (Tenant URL identifier)</label>
                <input
                  type="text"
                  placeholder="tanishq-jewellery"
                  value={slug}
                  onChange={(e) => setSlug(e.target.value)}
                  className="glass-input w-full px-4 py-2.5 mt-1 font-mono text-xs"
                  required
                />
              </div>

              <div>
                <label className="text-sm font-medium text-gray-300">Legal Company Name</label>
                <input
                  type="text"
                  placeholder="e.g. Titan Company Ltd."
                  value={legalName}
                  onChange={(e) => setLegalName(e.target.value)}
                  className="glass-input w-full px-4 py-2.5 mt-1"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-sm font-medium text-gray-300">Email</label>
                  <input
                    type="email"
                    placeholder="contact@store.com"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="glass-input w-full px-4 py-2 mt-1 text-sm"
                  />
                </div>
                <div>
                  <label className="text-sm font-medium text-gray-300">Phone</label>
                  <input
                    type="text"
                    placeholder="+919876543210"
                    value={phone}
                    onChange={(e) => setPhone(e.target.value)}
                    className="glass-input w-full px-4 py-2 mt-1 text-sm"
                  />
                </div>
              </div>

              <div className="flex gap-3 pt-4 border-t border-white/10">
                <button
                  type="button"
                  onClick={() => setShowCreateModal(false)}
                  className="flex-1 py-2.5 bg-white/5 hover:bg-white/10 text-gray-300 rounded-lg font-medium text-sm"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={saving}
                  className="flex-1 py-2.5 bg-gradient-gold text-white rounded-lg font-medium text-sm shadow-lg shadow-brand/20"
                >
                  {saving ? 'Onboarding...' : 'Onboard Store'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
