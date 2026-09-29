/**
 * API client for authentication endpoints.
 */

import { apiClient } from './client';

export const authApi = {
  /**
   * Get the current user's profile.
   * Used to verify token and get is_super_admin flag.
   */
  getMe: () => apiClient.get('/auth/me'),
};
