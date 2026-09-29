'use client';

import { useState, useEffect } from 'react';
import { Activity, Search, Shield, Eye, Calendar, User, Building2 } from 'lucide-react';
import { apiClient } from '@/lib/api/client';
import toast from 'react-hot-toast';

export default function AuditLogsPage() {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [searchAction, setSearchAction] = useState('');
  const [selectedLog, setSelectedLog] = useState(null);

  useEffect(() => {
    fetchLogs();
  }, [page, searchAction]);

  const fetchLogs = async () => {
    setLoading(true);
    try {
      let url = `/admin/audit-logs?page=${page}&page_size=15`;
      if (searchAction) url += `&action=${encodeURIComponent(searchAction)}`;
      const res = await apiClient.get(url);
      setLogs(res.data.data || []);
      setTotalPages(res.data.total_pages || 1);
    } catch (err) {
      toast.error('Failed to load audit logs');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-8 space-y-8 max-w-7xl mx-auto">
      <div>
        <h1 className="text-3xl font-display font-bold text-white flex items-center gap-3">
          <Activity className="w-8 h-8 text-amber-400" /> Platform Audit Trail
        </h1>
        <p className="text-gray-400 mt-1 text-sm">Immutable audit log of all administrative actions, organization status changes, and privilege updates</p>
      </div>

      {/* Filter Bar */}
      <div className="glass-card p-4 flex items-center gap-4">
        <div className="relative flex-1">
          <Search className="w-4 h-4 text-gray-400 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="Search by action (e.g. organization.created, subscription.assigned)..."
            value={searchAction}
            onChange={(e) => {
              setSearchAction(e.target.value);
              setPage(1);
            }}
            className="glass-input w-full pl-9 pr-4 py-2 text-sm"
          />
        </div>
      </div>

      {/* Table */}
      <div className="glass-card overflow-hidden">
        <table className="w-full text-left text-sm text-gray-300">
          <thead className="bg-white/5 text-xs uppercase font-semibold text-gray-400 border-b border-white/10">
            <tr>
              <th className="py-3.5 px-4">Action</th>
              <th className="py-3.5 px-4">Actor UUID</th>
              <th className="py-3.5 px-4">Entity Category</th>
              <th className="py-3.5 px-4">Timestamp</th>
              <th className="py-3.5 px-4 text-right">Metadata</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-white/5">
            {loading ? (
              <tr>
                <td colSpan={5} className="py-8 text-center text-gray-400">Loading audit records...</td>
              </tr>
            ) : logs.length === 0 ? (
              <tr>
                <td colSpan={5} className="py-8 text-center text-gray-400">No audit records found matching criteria.</td>
              </tr>
            ) : (
              logs.map((log) => (
                <tr key={log.id} className="hover:bg-white/5 transition-colors">
                  <td className="py-3.5 px-4 font-mono font-medium text-brand-light">
                    {log.action}
                  </td>
                  <td className="py-3.5 px-4 font-mono text-xs text-gray-400">
                    {log.actor_user_id ? `${log.actor_user_id.substring(0, 8)}...` : 'System'}
                  </td>
                  <td className="py-3.5 px-4">
                    <span className="px-2 py-0.5 rounded text-xs bg-white/10 font-mono">
                      {log.entity_type || 'platform'}
                    </span>
                  </td>
                  <td className="py-3.5 px-4 text-xs text-gray-400">
                    {new Date(log.created_at).toLocaleString()}
                  </td>
                  <td className="py-3.5 px-4 text-right">
                    <button
                      onClick={() => setSelectedLog(log)}
                      className="p-1.5 rounded bg-white/5 hover:bg-white/10 text-brand-light transition-colors"
                      title="View Details"
                    >
                      <Eye className="w-4 h-4" />
                    </button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>

        {/* Pagination */}
        <div className="p-4 border-t border-white/10 flex items-center justify-between text-xs text-gray-400">
          <span>Page {page} of {totalPages}</span>
          <div className="flex gap-2">
            <button
              disabled={page <= 1}
              onClick={() => setPage(p => p - 1)}
              className="px-3 py-1.5 rounded bg-white/5 hover:bg-white/10 disabled:opacity-50"
            >
              Previous
            </button>
            <button
              disabled={page >= totalPages}
              onClick={() => setPage(p => p + 1)}
              className="px-3 py-1.5 rounded bg-white/5 hover:bg-white/10 disabled:opacity-50"
            >
              Next
            </button>
          </div>
        </div>
      </div>

      {/* Metadata Detail Modal */}
      {selectedLog && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="glass-card w-full max-w-xl p-6 space-y-4">
            <div className="flex justify-between items-center border-b border-white/10 pb-3">
              <h3 className="text-lg font-bold text-white font-mono">{selectedLog.action}</h3>
              <button onClick={() => setSelectedLog(null)} className="text-gray-400 hover:text-white">✕</button>
            </div>

            <div className="space-y-2 text-xs text-gray-300">
              <p><strong className="text-gray-400">Audit ID:</strong> {selectedLog.id}</p>
              <p><strong className="text-gray-400">Actor ID:</strong> {selectedLog.actor_user_id || 'System'}</p>
              <p><strong className="text-gray-400">Organization ID:</strong> {selectedLog.organization_id || 'Platform Level'}</p>
              <p><strong className="text-gray-400">Recorded At:</strong> {new Date(selectedLog.created_at).toISOString()}</p>
            </div>

            <div className="space-y-1">
              <p className="text-xs font-semibold uppercase text-gray-400">Audit Metadata JSON:</p>
              <pre className="p-3 rounded bg-navy-dark border border-white/10 font-mono text-xs text-emerald-400 overflow-x-auto">
                {JSON.stringify(selectedLog.action_metadata, null, 2)}
              </pre>
            </div>

            <button
              onClick={() => setSelectedLog(null)}
              className="w-full py-2 bg-white/10 text-white rounded-lg text-sm font-medium hover:bg-white/20"
            >
              Close
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
