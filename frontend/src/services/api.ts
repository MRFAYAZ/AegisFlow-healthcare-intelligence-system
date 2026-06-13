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
  create: (data: unknown) => api.post('/inventory', data),
  update: (id: string, data: unknown) => api.put(`/inventory/${id}`, data),
  delete: (id: string) => api.delete(`/inventory/${id}`),
}

// Emergencies
export const emergencyAPI = {
  getAll: () => api.get('/emergencies'),
  activate: (id: string, data: unknown) => api.post(`/emergencies/${id}/activate`, data),
  resolve: (id: string) => api.post(`/emergencies/${id}/resolve`),
}

// Transfers
export const transferAPI = {
  getAll: () => api.get('/transfers'),
  create: (data: unknown) => api.post('/transfers', data),
  approve: (id: string) => api.post(`/transfers/${id}/approve`),
  markDelivered: (id: string) => api.post(`/transfers/${id}/delivered`),
}

// Shortages
export const shortageAPI = {
  getAll: () => api.get('/shortages'),
  source: (id: string) => api.post(`/shortages/${id}/source`),
}

// Analytics
export const analyticsAPI = {
  getDashboard: () => api.get('/analytics/dashboard'),
  getTrends: () => api.get('/analytics/trends'),
}

// Facilities
export const facilitiesAPI = {
  getAll: () => api.get('/facilities'),
  getNearby: (lat: number, lng: number, radius: number) =>
    api.get(`/facilities/nearby?lat=${lat}&lng=${lng}&radius=${radius}`),
}
