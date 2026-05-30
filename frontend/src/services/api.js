const BASE_URL = '/api';

async function request(endpoint, options = {}) {
  const url = `${BASE_URL}${endpoint}`;
  const headers = {
    'Content-Type': 'application/json',
    ...options.headers,
  };

  try {
    const response = await fetch(url, { ...options, headers });
    if (!response.ok) {
      let errorMessage = `HTTP error! Status: ${response.status}`;
      try {
        const errData = await response.json();
        errorMessage = errData.detail || errorMessage;
      } catch (_) {}
      throw new Error(errorMessage);
    }
    if (response.status === 204) {
      return null;
    }
    return await response.json();
  } catch (error) {
    console.error(`API Request to ${endpoint} failed:`, error);
    throw error;
  }
}

export const api = {
  // Dashboard stats
  fetchDashboardStats: () => request('/dashboard/summary'),
  fetchAlerts: () => request('/dashboard/alerts'),
  markAlertRead: (alertId) => request(`/dashboard/alerts/${alertId}/read`, { method: 'PUT' }),

  // Vendors
  fetchVendors: () => request('/vendors'),
  createVendor: (data) => request('/vendors', {
    method: 'POST',
    body: JSON.stringify(data),
  }),
  fetchVendor: (id) => request(`/vendors/${id}`),
  updateVendor: (id, data) => request(`/vendors/${id}`, {
    method: 'PUT',
    body: JSON.stringify(data),
  }),
  deleteVendor: (id) => request(`/vendors/${id}`, { method: 'DELETE' }),

  // Scans
  triggerScan: () => request('/scans/trigger', { method: 'POST' }),
  triggerVendorScan: (vendorId) => request(`/scans/trigger/${vendorId}`, { method: 'POST' }),
  fetchScanHistory: () => request('/scans/history'),
  fetchLatestResults: () => request('/scans/latest'),

  // Full report
  fetchVendorReport: (vendorId) => request(`/reports/${vendorId}`),
};
export default api;
