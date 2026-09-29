/**
 * useOrganization hook — fetches the current organization context.
 */

'use client';

import { useState, useEffect } from 'react';
import { organizationsApi } from '@/lib/api/organizations';

export function useOrganization(organizationId) {
  const [organization, setOrganization] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!organizationId) {
      setLoading(false);
      return;
    }

    const fetchOrganization = async () => {
      try {
        setLoading(true);
        const response = await organizationsApi.get(organizationId);
        setOrganization(response.data.data);
      } catch (err) {
        setError(err.response?.data?.message || 'Failed to load organization');
      } finally {
        setLoading(false);
      }
    };

    fetchOrganization();
  }, [organizationId]);

  return { organization, loading, error };
}
