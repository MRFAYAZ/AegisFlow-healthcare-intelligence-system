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
  getShortagePredictions: () => api.get('/inventory/shortage-predictions'),
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
  // --- ADDED: The new endpoint for AI Donor Ranking ---
  getMatches: (id: string) => api.get(`/emergencies/${id}/matches`),
  getAllocation: (id: string) => api.get(`/emergencies/${id}/allocation`),
  approveAllocation: (id: string, lines: unknown[]) =>
    api.post(`/emergencies/${id}/allocation/approve`, { lines }),
  rejectAllocation: (id: string) => api.post(`/emergencies/${id}/allocation/reject`),
}

export const auditAPI = {
  getEmergencyTimeline: (emergencyId: string) =>
    api.get(`/audit-logs/emergency/${emergencyId}`),
}

// Transfers
export const transferAPI = {
  getAll: () => api.get('/transfers'),
  create: (data: unknown) => api.post('/transfers', data),
  approve: (id: string, approved_quantity: number) => api.post(`/redistribution/${id}/approve`, { approved_quantity }),
  markDelivered: (id: string) => api.post(`/redistribution/${id}/dispatch/delivered`),
}

// Shortages
export const shortageAPI = {
  getAll: () => api.get('/shortages'),
  source: (id: string) => api.post(`/shortages/${id}/source`),
}

export const procurementAPI = {
  getRequirements: () => api.get('/procurement/replenishment'),
  getSuppliers: (medicineId: string, targetFacilityId: string, requestedQuantity: number) => api.get(`/procurement/suppliers/${medicineId}?target_facility_id=${targetFacilityId}&requested_quantity=${requestedQuantity}`),
  createSupplyRequest: (data: { inventory_id: string; supplier_facility_id: string; requested_quantity: number }) => api.post('/procurement/supply-requests', data),
  getSupplyRequests: () => api.get('/procurement/supply-requests'),
  decideSupplyRequest: (id: string, acceptedQuantity: number) => api.post(`/procurement/supply-requests/${id}/decision`, { accepted_quantity: acceptedQuantity }),
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

  assignDispatch: (transferId: string, payload: { transport_type: string; vehicle_reference?: string | null }) =>
    api.post(`/redistribution/${transferId}/dispatch/assign`, payload),

  startDispatch: (transferId: string) =>
    api.post(`/redistribution/${transferId}/dispatch`),

  markDelivered: (transferId: string) =>
    api.post(`/redistribution/${transferId}/dispatch/delivered`),

  getDispatchStatus: (transferId: string) =>
    api.get(`/redistribution/${transferId}/dispatch`),

  dispatch: (emergencyCaseId: string) =>
    api.post('/redistribution/dispatch', { emergency_case_id: emergencyCaseId }),
}

export const dispatchAPI = {
  getDashboard: () => api.get('/dispatch/dashboard'),
  assign: (
    transferId: string,
    data: { transport_type: string; vehicle_reference?: string },
  ) => api.post(`/dispatch/${transferId}/assign`, data),
  dispatch: (transferId: string) => api.post(`/dispatch/${transferId}/dispatch`),
  delivered: (transferId: string) => api.post(`/dispatch/${transferId}/delivered`),
}