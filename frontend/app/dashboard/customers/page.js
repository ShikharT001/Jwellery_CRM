'use client';

import { Users, Sparkles } from 'lucide-react';

export const dynamic = 'force-dynamic';

export default function CustomersPlaceholderPage() {
  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-display font-bold text-white flex items-center gap-3">
          <Users className="w-8 h-8 text-brand-light" /> Customer Relationship Management
        </h1>
        <p className="text-gray-400 mt-1 text-sm">Customer profiles, purchase history, and scheme tracking</p>
      </div>

      <div className="glass-card p-12 flex flex-col items-center justify-center text-center space-y-4 max-w-2xl mx-auto my-12 border border-brand/20">
        <div className="w-16 h-16 rounded-2xl bg-brand/10 border border-brand/30 flex items-center justify-center text-brand-light">
          <Sparkles className="w-8 h-8 animate-pulse" />
        </div>
        <h2 className="text-2xl font-bold text-white font-display">Customer CRM Module</h2>
        <p className="text-gray-300 text-sm max-w-md">
          Customer profiles and purchase history will be integrated in Phase 4.
        </p>
      </div>
    </div>
  );
}
