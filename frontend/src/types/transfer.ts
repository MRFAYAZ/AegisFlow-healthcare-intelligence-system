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
