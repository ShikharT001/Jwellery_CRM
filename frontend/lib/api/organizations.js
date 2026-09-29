/**
 * API client for organizations endpoints.
 * Uses the authenticated Axios instance.
 */

import { apiClient } from './client';

export const organizationsApi = {
  /**
   * List all organizations (Super Admin only)
   */
  list: (params = {}) =>
    apiClient.get('/organizations', { params }),

  /**
   * Create a new organization (Super Admin only)
   */
  create: (data) =>
    apiClient.post('/organizations', data),

  /**
   * Get a single organization by ID
   */
  get: (id) =>
    apiClient.get(`/organizations/${id}`),

  /**
   * Update organization details
   */
  update: (id, data) =>
    apiClient.patch(`/organizations/${id}`, data),

  /**
   * Change organization status (suspend/activate/etc.)
   */
  updateStatus: (id, status, reason) =>
    apiClient.patch(`/organizations/${id}/status`, { status, reason }),

  /**
   * List branches for an organization
   */
  listBranches: (orgId, params = {}) =>
    apiClient.get(`/organizations/${orgId}/branches`, { params }),

  /**
   * Create a branch
   */
  createBranch: (orgId, data) =>
    apiClient.post(`/organizations/${orgId}/branches`, data),

  /**
   * Update a branch
   */
  updateBranch: (orgId, branchId, data) =>
    apiClient.patch(`/organizations/${orgId}/branches/${branchId}`, data),
};
