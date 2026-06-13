import { createBrowserRouter, RouterProvider, Navigate } from 'react-router-dom'
import { AppLayout } from '../components/layout/AppLayout'
import { LoginPage } from '../pages/auth/LoginPage'
import { DashboardPage } from '../pages/dashboard/DashboardPage'
import { EmergencyPage } from '../pages/emergency/EmergencyPage'
import { InventoryPage } from '../pages/inventory/InventoryPage'
import { ShortagePage } from '../pages/shortage/ShortagePage'
import { TransfersPage } from '../pages/transfers/TransfersPage'
import { AnalyticsPage } from '../pages/analytics/AnalyticsPage'
import { MapPage } from '../pages/map/MapPage'
import { ShopPage } from '../pages/shop/ShopPage'

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const token = localStorage.getItem('aegisflow_token')
  if (!token) return <Navigate to="/login" replace />
  return <>{children}</>
}

const router = createBrowserRouter([
  { path:'/login', element:<LoginPage /> },
  {
    path:'/',
    element:<ProtectedRoute><AppLayout /></ProtectedRoute>,
    children:[
      { index: true, element:<Navigate to="/dashboard" replace /> },
      { path:'dashboard', element:<DashboardPage /> },
      { path:'emergency', element:<EmergencyPage /> },
      { path:'inventory', element:<InventoryPage /> },
      { path:'shortage', element:<ShortagePage /> },
      { path:'transfers', element:<TransfersPage /> },
      { path:'analytics', element:<AnalyticsPage /> },
      { path:'map', element:<MapPage /> },
      { path:'shop', element:<ShopPage /> },
    ]
  },
  { path:'*', element:<Navigate to="/dashboard" replace /> },
])

export function AppRouter() {
  return <RouterProvider router={router} />
}
