export type Role = 'system_admin' | 'hospital_admin' | 'pharmacist' | 'shop_owner' | 'emergency_operator'

export interface User {
  id: string
  name: string
  email: string
  role: string
  facility?: string
  avatar?: string
}

export interface Medicine {
  id: string
  name: string
  details: string
  category: string
  stock: number
  maxStock: number
  expiry: string
  status: 'adequate' | 'warning' | 'critical' | 'emergency'
  unit: string
}

export interface Emergency {
  id: string
  medicine: string
  facility: string
  units: number
  severity: 'emergency' | 'critical'
  donor: string
  donorUnits: number
  distance: string
  eta: string
  status: 'pending' | 'in_transit' | 'sourcing' | 'resolved'
}

export interface Transfer {
  id: string
  medicine: string
  from: string
  to: string
  quantity: string
  status: 'pending' | 'in_transit' | 'delivered' | 'sourcing'
  eta: string
  createdAt: string
}

export interface Shortage {
  id: string
  medicine: string
  facility: string
  severity: 'emergency' | 'critical' | 'warning'
  stock: string
  daysLeft: number
  nearestSource: string
}

export interface KPI {
  label: string
  value: string | number
  sub: string
  trend?: 'up' | 'down' | 'neutral'
  color: 'blue' | 'green' | 'red' | 'orange'
}

export interface Alert {
  id: string
  type: 'emergency' | 'critical' | 'warning' | 'resolved'
  message: string
  time: string
}

export interface Facility {
  id: string
  name: string
  type: 'hospital' | 'pharmacy' | 'clinic'
  lat: number
  lng: number
  status: 'stocked' | 'low' | 'critical' | 'emergency'
  address: string
}
