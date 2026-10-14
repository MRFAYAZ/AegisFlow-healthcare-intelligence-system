import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1',
  timeout: 10000,
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('aegisflow_token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

api.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401) {
      localStorage.removeItem('aegisflow_token')
      window.location.href = '/login'
    }
    return Promise.reject(err)
  }
)

export default api

// Auth
export const authAPI = {
  login: (email: string, password: string) => api.post('/auth/login', { email, password }),
  logout: () => api.post('/auth/logout'),
  me: () => api.get('/auth/me'),
}

// Inventory
export const inventoryAPI = {
  getAll: () => api.get('/inventory'),
  getForecast: () => api.get('/inventory/forecast'),
  create: (data: unknown) => api.post('/inventory', data),
  update: (id: string, data: unknown) => api.put(`/inventory/${id}`, data),
  delete: (id: string) => api.delete(`/inventory/${id}`),
}

// Emergencies
export const emergencyAPI = {
  getAll: () => api.get('/emergencies'),
  getActive: () => api.get('/emergencies/active'),
  getCritical: () => api.get('/emergencies/critical'),
  getDashboard: () => api.get('/emergencies/dashboard'),
  getMatches: (emergencyCaseId: string, maxDistanceKm?: number) =>
    api.get(`/emergencies/${emergencyCaseId}/matches`, {
      params: maxDistanceKm ? { max_distance_km: maxDistanceKm } : undefined,
    }),
  getTimeline: (emergencyCaseId: string) =>
    api.get(`/emergencies/${emergencyCaseId}/timeline`),
}

// Transfers
export const transferAPI = {
  getAll: () => api.get('/redistribution'),
  approve: (id: string, approvedQuantity: number) =>
    api.post(`/redistribution/${id}/approve`, { approved_quantity: approvedQuantity }),
  reject: (id: string, reason: string) =>
    api.post(`/redistribution/${id}/reject`, { reason }),
  assignDispatch: (id: string, transportType: string, vehicleReference?: string) =>
    api.post(`/redistribution/${id}/assign`, {
      transport_type: transportType,
      vehicle_reference: vehicleReference || undefined,
    }),
  dispatch: (id: string) => api.post(`/redistribution/${id}/dispatch`),
  markDelivered: (id: string) => api.post(`/redistribution/${id}/delivered`),
}

// Shortages
export const shortageAPI = {
  getAll: () => api.get('/shortages'),
  source: (id: string) => api.post(`/shortages/${id}/source`),
}

// Analytics
export const analyticsAPI = {
  getDashboard: () => api.get('/dashboard/review')
}

// Facilities
export const facilitiesAPI = {
  getAll: () => api.get('/facilities'),
  getNearby: (lat: number, lng: number, radius: number) =>
    api.get(`/facilities/nearby?lat=${lat}&lng=${lng}&radius=${radius}`),
}

export const redistributionAPI = {
  getAll: () =>
    api.get('/redistribution'),

  getDashboard: () =>
    api.get('/redistribution/dashboard'),

  getHighPriority: () =>
    api.get('/redistribution/high-priority'),

  requestTransfer: (emergencyCaseId: string) =>
    api.post('/redistribution/request', { emergency_case_id: emergencyCaseId }),
  // Backwards-compatible alias; the backend treats this as a request, not a shipment dispatch.
  dispatch: (emergencyCaseId: string) =>
    api.post('/redistribution/request', { emergency_case_id: emergencyCaseId }),
}