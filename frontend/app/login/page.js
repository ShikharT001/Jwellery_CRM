'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { Gem } from 'lucide-react';
import { supabase } from '@/lib/auth/supabaseClient';
import toast from 'react-hot-toast';

export default function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const router = useRouter();

  const handleLogin = async (e) => {
    e.preventDefault();
    setLoading(true);
    
    const { error } = await supabase.auth.signInWithPassword({
      email,
      password,
    });
    
    if (error) {
      toast.error(error.message);
      setLoading(false);
    } else {
      toast.success('Login successful');
      router.push('/dashboard');
    }
  };

  return (
    <div className="min-h-screen bg-navy relative flex items-center justify-center overflow-hidden">
      {/* Animated gold particle background effect */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-1/2 -left-1/2 w-[200%] h-[200%] opacity-10 bg-[radial-gradient(circle_at_center,_var(--tw-gradient-stops))] from-brand-light via-navy to-navy" />
      </div>

      <div className="glass-card w-full max-w-md p-8 relative z-10 animate-fade-in mx-4">
        <div className="flex flex-col items-center mb-8">
          <div className="w-16 h-16 rounded-2xl bg-white/5 border border-white/10 flex items-center justify-center mb-4 shadow-lg shadow-brand/20">
            <Gem className="w-8 h-8 text-brand-light" />
          </div>
          <h1 className="text-3xl font-display font-bold text-gradient-gold">JewelERP</h1>
          <p className="text-gray-400 mt-2 text-sm text-center">Premium Jewellery Business Platform</p>
        </div>

        <form onSubmit={handleLogin} className="space-y-6">
          <div className="space-y-2">
            <label className="text-sm font-medium text-gray-300">Email Address</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="glass-input w-full px-4 py-3"
              placeholder="admin@example.com"
              required
            />
          </div>
          <div className="space-y-2">
            <div className="flex justify-between items-center">
              <label className="text-sm font-medium text-gray-300">Password</label>
              <a href="#" className="text-xs text-brand-light hover:text-brand-bright transition-colors">Forgot Password?</a>
            </div>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="glass-input w-full px-4 py-3"
              placeholder="••••••••"
              required
            />
          </div>
          
          <button
            type="submit"
            disabled={loading}
            className="w-full py-3 px-4 bg-gradient-gold text-white font-medium rounded-lg hover:shadow-lg hover:shadow-brand/20 transition-all active:scale-[0.98] disabled:opacity-70 disabled:cursor-not-allowed flex items-center justify-center"
          >
            {loading ? (
              <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
            ) : (
              'Sign In'
            )}
          </button>
        </form>
      </div>
    </div>
  );
}
