import { useState } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'
import { toast } from 'sonner'
import { Bell, Check, Monitor, Moon, Search, Settings, Sun } from 'lucide-react'
import { useEmergencies } from '../../hooks/useEmergency'
import { useAppStore } from '../../store/useAppStore'
import type { ThemePreference } from '../../store/useAppStore'

const pageTitles: Record<string, string> = {
  '/dashboard': 'Command center',
  '/emergency': 'Emergency operations',
  '/inventory': 'Inventory management',
  '/shortage':  'Shortage Intelligence',
  '/transfers': 'Transfer center',
  '/analytics': 'Analytics & intelligence',
  '/map':       'Geospatial map',
  '/shop':      'Medical shop',
  '/procurement': 'Supply Intelligence',
}

export function Topbar() {
  const { pathname } = useLocation()
  const navigate = useNavigate()
  const user = useAppStore((state) => state.user)
  const theme = useAppStore((state) => state.theme)
  const setTheme = useAppStore((state) => state.setTheme)
  const { data: emergencies = [] } = useEmergencies()
  const [notifsOpen, setNotifsOpen] = useState(false)
  const [settingsOpen, setSettingsOpen] = useState(false)
  const [search, setSearch] = useState('')
  const [allRead, setAllRead] = useState(false)
  const title = pageTitles[pathname] || 'AegisFlow'
  const unread = allRead ? 0 : emergencies.filter((emergency) => emergency.emergency_status !== 'RESOLVED').length

  function submitSearch(event: React.FormEvent) {
    event.preventDefault()
    const query = search.trim().toLowerCase()
    const route = query.includes('emerg') ? '/emergency'
      : query.includes('invent') || query.includes('medicine') ? '/inventory'
        : query.includes('short') || query.includes('risk') ? '/shortage'
          : query.includes('transfer') ? '/transfers'
            : query.includes('dispatch') || query.includes('vehicle') ? '/dispatcher'
              : query.includes('map') || query.includes('facility') ? '/map'
                : query.includes('analytic') || query.includes('report') ? '/analytics'
                  : null

    if (!route) {
      toast.error('Search by emergency, inventory, shortage, transfer, dispatch, map or analytics')
      return
    }

    navigate(route)
    setSearch('')
  }

  function logout() {
    localStorage.removeItem('aegisflow_token')
    useAppStore.getState().setUser(null)
    navigate('/login')
  }

  return (
    <header className="h-12 bg-white border-b border-border flex items-center px-5 gap-3 flex-shrink-0">
      <div className="text-[14px] font-semibold text-ink flex-1">{title}</div>

      {/* Search */}
      <form onSubmit={submitSearch} className="flex items-center gap-2 bg-surface-muted border border-border rounded px-3 py-1.5 w-56 text-ink-faint text-[12px] focus-within:border-border-strong">
        <Search size={15} aria-hidden="true" />
        <input aria-label="Search workspace" value={search} onChange={(event) => setSearch(event.target.value)} placeholder="Search workspace..." className="min-w-0 flex-1 bg-transparent outline-none text-ink" />
      </form>

      {/* Notif */}
      <div className="relative">
        <button
          className="w-8 h-8 rounded border border-border bg-white flex items-center justify-center text-ink-muted hover:bg-surface-muted relative"
          onClick={() => setNotifsOpen(p => !p)}
        >
          <Bell size={16} aria-hidden="true" />
          {unread > 0 && (
            <span className="absolute top-1 right-1 w-1.5 h-1.5 rounded-full bg-status-red border border-white" />
          )}
        </button>

        {notifsOpen && (
          <div className="absolute top-10 right-0 w-72 bg-white border border-border rounded-xl shadow-lg z-50">
            <div className="flex items-center justify-between px-3 py-2.5 border-b border-border">
              <span className="text-[12px] font-semibold text-ink">Notifications</span>
              <button onClick={() => { setAllRead(true); setNotifsOpen(false) }} className="text-[11px] text-blue-600">Mark all read</button>
            </div>
            {emergencies.length === 0 && <div className="px-3 py-4 text-[11px] text-ink-faint">No active emergency notifications.</div>}
            {emergencies.filter((emergency) => emergency.emergency_status !== 'RESOLVED').slice(0, 5).map((emergency) => (
              <div key={emergency.emergency_case_id} className="flex gap-2.5 px-3 py-2.5 border-b border-border last:border-b-0 hover:bg-surface-muted cursor-pointer" onClick={() => { navigate('/emergency'); setNotifsOpen(false) }}>
                <div className={`w-1.5 h-1.5 rounded-full flex-shrink-0 mt-1.5`}
                  style={{ background: allRead ? '#9a9890' : emergency.severity === 'EMERGENCY' ? '#dc2626' : '#ea580c' }} />
                <div>
                  <div className="text-[11px] text-ink leading-snug">{emergency.medicine_name} shortage at {emergency.facility_name}</div>
                  <div className="text-[10px] text-ink-faint mt-0.5">{emergency.emergency_status}</div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Settings */}
      <div className="relative">
        <button aria-label="Open settings" onClick={() => setSettingsOpen((open) => !open)} className="icon-button" aria-expanded={settingsOpen}>
          <Settings size={16} aria-hidden="true" />
        </button>
        {settingsOpen && (
          <div className="settings-menu absolute top-11 right-0 z-50 w-64 rounded-xl border border-border bg-white p-3 shadow-lg">
            <div className="border-b border-border pb-2">
              <div className="text-[12px] font-semibold text-ink">{user?.name || 'User settings'}</div>
              <div className="text-[10px] text-ink-faint">{user?.email || 'No profile loaded'}</div>
            </div>
            <div className="mt-3">
              <div className="mb-2 text-[10px] font-semibold uppercase tracking-[0.08em] text-ink-faint">Appearance</div>
              <div className="theme-options" role="group" aria-label="Theme preference">
                {([
                  ['system', 'System default', Monitor],
                  ['light', 'Light', Sun],
                  ['dark', 'Dark', Moon],
                ] as const).map(([value, label, Icon]) => (
                  <button key={value} className={`theme-option ${theme === value ? 'selected' : ''}`} onClick={() => setTheme(value as ThemePreference)}>
                    <Icon size={14} aria-hidden="true" />
                    <span>{label}</span>
                    {theme === value && <Check size={14} className="ml-auto" aria-hidden="true" />}
                  </button>
                ))}
              </div>
            </div>
            <button className="mt-2 w-full rounded px-2 py-2 text-left text-[11px] text-ink hover:bg-surface-muted" onClick={() => window.location.reload()}>Refresh workspace</button>
            <button className="w-full rounded px-2 py-2 text-left text-[11px] text-red-600 hover:bg-red-50" onClick={logout}>Sign out</button>
          </div>
        )}
      </div>

      {/* Status */}
      <div className="flex items-center gap-1.5 px-3 py-1 rounded-full bg-green-50 border border-green-200 text-[11px] font-medium text-green-700">
        <span className="w-1.5 h-1.5 rounded-full bg-green-500 inline-block" />
        All systems normal
      </div>
    </header>
  )
}
