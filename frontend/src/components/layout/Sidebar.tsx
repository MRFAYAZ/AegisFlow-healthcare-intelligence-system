import { NavLink, useNavigate } from 'react-router-dom'
import { Activity, AlertTriangle, ArrowLeftRight, BarChart3, Boxes, BusFront, LayoutDashboard, Map, ShoppingCart } from 'lucide-react'
import { useEmergencies } from '../../hooks/useEmergency'
import { useAppStore } from '../../store/useAppStore'
import { canAccessRoute, getWorkspace, type AppRoute } from '../../auth/rolePermissions'

const routeMeta: Record<AppRoute, { icon: typeof Activity; label: string; badge?: number; badgeType?: 'red' | 'orange' }> = {
  '/dashboard': { icon: LayoutDashboard, label: 'Dashboard' },
  '/emergency': { icon: AlertTriangle, label: 'Emergency operations', badge: 3, badgeType: 'red' },
  '/inventory': { icon: Boxes, label: 'Inventory' },
  '/shortage': { icon: Activity, label: 'Shortage Intelligence', badge: 7, badgeType: 'orange' },
  '/transfers': { icon: ArrowLeftRight, label: 'Transfers' },
  '/dispatcher': { icon: BusFront, label: 'Dispatch control' },
  '/analytics': { icon: BarChart3, label: 'Analytics' },
  '/map': { icon: Map, label: 'Situation map' },
  '/shop': { icon: ShoppingCart, label: 'Supply requests' },
  '/procurement': { icon: ShoppingCart, label: 'Supply Intelligence' },
}

export function Sidebar() {
  const user = useAppStore((state) => state.user)
  const workspace = getWorkspace(user?.role)
  const navigate = useNavigate()
  const { data: emergencies = [] } = useEmergencies()
  const activeEmer = emergencies.length

  function logout() {
    localStorage.removeItem('aegisflow_token')
    useAppStore.getState().setUser(null)
    navigate('/login')
  }

  return (
    <aside style={{ width:224 }} className="app-sidebar flex flex-col flex-shrink-0 h-full border-r">
      {/* Logo */}
      <div className="flex items-center gap-2.5 px-4 py-4 border-b border-border">
        <div className="w-8 h-8 bg-blue-700 rounded-lg flex items-center justify-center flex-shrink-0">
          <span className="text-white text-sm font-bold">A</span>
        </div>
        <div className="brand-copy">
          <div className="text-[14px] font-semibold text-ink">AegisFlow</div>
          <div className="text-[10px] text-ink-faint">{workspace?.name || 'Healthcare Intelligence'}</div>
        </div>
      </div>

      {/* Nav */}
      <nav className="flex-1 overflow-y-auto py-2">
        {(workspace?.sections ?? []).map((section) => (
          <div key={section.name} className="px-2 mb-1">
            <div className="text-[10px] text-ink-faint uppercase tracking-[0.5px] px-2 py-2">{section.name}</div>
            {section.routes.filter((route) => canAccessRoute(user?.role, route)).map((route) => {
              const item = routeMeta[route]
              const liveCount = route === '/emergency' ? activeEmer : item.badge
              return (
                <NavLink
                  key={route}
                  to={route}
                  className={({ isActive }) =>
                    `nav-item ${isActive ? 'active' : ''}`
                  }
                >
                  <item.icon size={16} strokeWidth={1.8} className="w-5" aria-hidden="true" />
                  <span className="nav-copy flex-1">{item.label}</span>
                  {liveCount !== undefined && liveCount > 0 && (
                    <span className={`nav-badge nav-badge-${item.badgeType}`}>
                      {liveCount}
                    </span>
                  )}
                </NavLink>
              )
            })}
          </div>
        ))}
      </nav>

      {/* User row */}
      <div className="p-3 border-t border-border">
        <div className="flex items-center gap-2 p-2 rounded hover:bg-surface-muted cursor-pointer group">
          <div className="w-7 h-7 rounded-full bg-blue-50 border border-blue-200 flex items-center justify-center text-blue-700 text-[11px] font-semibold flex-shrink-0">
            {user?.name?.slice(0,2).toUpperCase() || 'SA'}
          </div>
          <div className="user-copy flex-1 min-w-0">
            <div className="text-[12px] font-medium text-ink truncate">{user?.name || 'Dr. S. Aryan'}</div>
            <div className="text-[10px] text-ink-faint capitalize">{user?.role?.replace('_',' ') || 'System admin'}</div>
          </div>
          <button onClick={logout} className="text-[10px] text-ink-faint hover:text-ink opacity-0 group-hover:opacity-100 transition-opacity">Out</button>
        </div>
      </div>
    </aside>
  )
}
