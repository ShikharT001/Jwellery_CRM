'use client';

import { createContext, useContext, useEffect, useState } from 'react';
import { supabase } from './supabaseClient';
import { apiClient } from '../api/client';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [session, setSession] = useState(null);
  const [loading, setLoading] = useState(true);
  const [isSuperAdmin, setIsSuperAdmin] = useState(false);

  useEffect(() => {
    const fetchSession = async () => {
      const { data: { session } } = await supabase.auth.getSession();
      setSession(session);
      
      if (session?.user) {
        await fetchProfile(session.user);
      } else {
        setLoading(false);
      }
    };

    fetchSession();

    const { data: { subscription } } = supabase.auth.onAuthStateChange(async (_event, session) => {
      setSession(session);
      if (session?.user) {
        await fetchProfile(session.user);
      } else {
        setUser(null);
        setIsSuperAdmin(false);
        setLoading(false);
      }
    });

    return () => {
      subscription.unsubscribe();
    };
  }, []);

  const fetchProfile = async (authUser) => {
    try {
      // Set default immediately for snappier UI
      setUser({
        id: authUser.id,
        email: authUser.email,
        display_name: authUser.email.split('@')[0],
        is_super_admin: false,
      });
      
      // Fetch rich profile from our backend
      // Response shape: { success: true, data: { id, email, display_name, is_super_admin, status } }
      const res = await apiClient.get('/auth/me');
      if (res.data?.data) {
        const profile = res.data.data;
        setUser(profile);
        setIsSuperAdmin(profile.is_super_admin || false);
      }
    } catch (error) {
      // Backend not reachable — keep using Supabase auth user
      console.warn('Backend profile fetch failed, using Supabase auth data:', error.message);
    } finally {
      setLoading(false);
    }
  };

  const logout = async () => {
    await supabase.auth.signOut();
  };

  const value = {
    user,
    session,
    loading,
    logout,
    isAuthenticated: !!user,
    isSuperAdmin
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => useContext(AuthContext);
