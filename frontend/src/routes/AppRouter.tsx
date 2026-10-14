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
import { ProcurementPage } from '../pages/procurement/ProcurementPage'
import { DispatcherDashboardPage } from '../pages/dispatcher/DispatcherDashboardPage'
import { RouteErrorPage } from '../pages/error/RouteErrorPage'
import { useAppStore } from '../store/useAppStore'
import { canAccessRoute, getWorkspace, type AppRoute } from '../auth/rolePermissions'

function ProtectedRoute({ children, route }: { children: React.ReactNode; route?: AppRoute }) {
  const token = localStorage.getItem('aegisflow_token')
  if (!token) return <Navigate to="/login" replace />

  const user = useAppStore((state) => state.user)
  if (!user) return <Navigate to="/login" replace />

  if (route && !canAccessRoute(user?.role, route)) {
    return <Navigate to="/dashboard" replace />
  }

  return <>{children}</>
}

function RoleLandingRedirect() {
  const user = useAppStore((state) => state.user)
  return <Navigate to={getWorkspace(user?.role)?.landingRoute ?? '/dashboard'} replace />
}

const router = createBrowserRouter([
  { path:'/login', element:<LoginPage />, errorElement:<RouteErrorPage /> },
  {
    path:'/',
    element:<ProtectedRoute><AppLayout /></ProtectedRoute>,
    children:[
      { index: true, element:<RoleLandingRedirect /> },
      { path:'dashboard', element:<ProtectedRoute route="/dashboard"><DashboardPage /></ProtectedRoute> },
      { path:'emergency', element:<ProtectedRoute route="/emergency"><EmergencyPage /></ProtectedRoute> },
      { path:'inventory', element:<ProtectedRoute route="/inventory"><InventoryPage /></ProtectedRoute> },
      { path:'shortage', element:<ProtectedRoute route="/shortage"><ShortagePage /></ProtectedRoute> },
      { path:'transfers', element:<ProtectedRoute route="/transfers"><TransfersPage /></ProtectedRoute> },
      { path:'dispatcher', element:<ProtectedRoute route="/dispatcher"><DispatcherDashboardPage /></ProtectedRoute> },
      { path:'analytics', element:<ProtectedRoute route="/analytics"><AnalyticsPage /></ProtectedRoute> },
      { path:'map', element:<ProtectedRoute route="/map"><MapPage /></ProtectedRoute> },
      { path:'shop', element:<ProtectedRoute route="/shop"><ShopPage /></ProtectedRoute> },
      { path:'procurement', element:<ProtectedRoute route="/procurement"><ProcurementPage /></ProtectedRoute> },
    ],
    errorElement:<RouteErrorPage />,
  },
  { path:'*', element:<Navigate to="/dashboard" replace /> },
])

export function AppRouter() {
  return <RouterProvider router={router} />
}
