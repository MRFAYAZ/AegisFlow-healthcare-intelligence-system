import { NavLink, useNavigate } from 'react-router-dom'
import { useAppStore } from '../../store/useAppStore'

const navItems = [
  { section:'Overview', items:[
    { to:'/dashboard', icon:'⊞', label:'Dashboard' },
    { to:'/emergency', icon:'⚠', label:'Emergency ops', badge:3, badgeType:'red' as const },
  ]},
  { section:'Hospital', items:[
    { to:'/inventory', icon:'▦', label:'Inventory' },
    { to:'/shortage', icon:'◉', label:'Shortages', badge:7, badgeType:'orange' as const },
    { to:'/transfers', icon:'⇅', label:'Transfers' },
  ]},
  { section:'Intelligence', items:[
    { to:'/analytics', icon:'▤', label:'Analytics' },
    { to:'/map', icon:'⊙', label:'Geo map' },
  ]},
  { section:'Pharmacy', items:[
    { to:'/shop', icon:'⊕', label:'Med shop' },
  ]},
]

export function Sidebar() {
  const { user, setUser } = useAppStore()
  const navigate = useNavigate()
  const { emergencies } = useAppStore()
  const activeEmer = emergencies.filter(e => e.status !== 'resolved').length

  function logout() {
    localStorage.removeItem('aegisflow_token')
    setUser(null)
    navigate('/login')
  }

  return (
    <aside style={{ width:224 }} className="bg-white border-r border-border flex flex-col flex-shrink-0 h-full">
      {/* Logo */}
      <div className="flex items-center gap-2.5 px-4 py-4 border-b border-border">
        <div className="w-8 h-8 bg-blue-700 rounded-lg flex items-center justify-center flex-shrink-0">
          <span className="text-white text-sm font-bold">A</span>
        </div>
        <div>
          <div className="text-[14px] font-semibold text-ink">AegisFlow</div>
          <div className="text-[10px] text-ink-faint">Healthcare Intelligence</div>
        </div>
      </div>

      {/* Nav */}
      <nav className="flex-1 overflow-y-auto py-2">
        {navItems.map((section) => (
          <div key={section.section} className="px-2 mb-1">
            <div className="text-[10px] text-ink-faint uppercase tracking-[0.5px] px-2 py-2">{section.section}</div>
            {section.items.map((item) => {
              const liveCount = item.to === '/emergency' ? activeEmer : item.badge
              return (
                <NavLink
                  key={item.to}
                  to={item.to}
                  className={({ isActive }) =>
                    `nav-item ${isActive ? 'active' : ''}`
                  }
                >
                  <span className="text-[15px] w-5 text-center">{item.icon}</span>
                  <span className="flex-1">{item.label}</span>
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
          <div className="flex-1 min-w-0">
            <div className="text-[12px] font-medium text-ink truncate">{user?.name || 'Dr. S. Aryan'}</div>
            <div className="text-[10px] text-ink-faint capitalize">{user?.role?.replace('_',' ') || 'System admin'}</div>
          </div>
          <button onClick={logout} className="text-[10px] text-ink-faint hover:text-ink opacity-0 group-hover:opacity-100 transition-opacity">Out</button>
        </div>
      </div>
    </aside>
  )
}
