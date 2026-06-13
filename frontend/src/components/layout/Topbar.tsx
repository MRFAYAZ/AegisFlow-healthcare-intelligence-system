import { useState } from 'react'
import { useLocation } from 'react-router-dom'

const pageTitles: Record<string, string> = {
  '/dashboard': 'Command center',
  '/emergency': 'Emergency operations',
  '/inventory': 'Inventory management',
  '/shortage':  'Shortage intelligence',
  '/transfers': 'Transfer center',
  '/analytics': 'Analytics & intelligence',
  '/map':       'Geospatial map',
  '/shop':      'Medical shop',
}

const notifications = [
  { id:1, type:'red', text:'Emergency: Zero Epinephrine at City General', time:'2 min ago', read:false },
  { id:2, type:'orange', text:'Insulin critically low — Apollo KMG', time:'18 min ago', read:false },
  { id:3, type:'muted', text:'Transfer #TF-2841 delivered successfully', time:'3 hr ago', read:true },
]

export function Topbar() {
  const { pathname } = useLocation()
  const [notifsOpen, setNotifsOpen] = useState(false)
  const [allRead, setAllRead] = useState(false)
  const title = pageTitles[pathname] || 'AegisFlow'
  const unread = allRead ? 0 : notifications.filter(n => !n.read).length

  return (
    <header className="h-12 bg-white border-b border-border flex items-center px-5 gap-3 flex-shrink-0">
      <div className="text-[14px] font-semibold text-ink flex-1">{title}</div>

      {/* Search */}
      <div className="flex items-center gap-2 bg-surface-muted border border-border rounded px-3 py-1.5 w-48 text-ink-faint text-[12px] cursor-pointer hover:border-border-strong">
        <span className="text-[13px]">🔍</span>
        Search…
      </div>

      {/* Notif */}
      <div className="relative">
        <button
          className="w-8 h-8 rounded border border-border bg-white flex items-center justify-center text-ink-muted hover:bg-surface-muted relative"
          onClick={() => setNotifsOpen(p => !p)}
        >
          🔔
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
            {notifications.map(n => (
              <div key={n.id} className="flex gap-2.5 px-3 py-2.5 border-b border-border last:border-b-0 hover:bg-surface-muted cursor-pointer" onClick={() => setNotifsOpen(false)}>
                <div className={`w-1.5 h-1.5 rounded-full flex-shrink-0 mt-1.5`}
                  style={{ background: allRead || n.read ? '#9a9890' : n.type==='red' ? '#dc2626' : '#ea580c' }} />
                <div>
                  <div className="text-[11px] text-ink leading-snug">{n.text}</div>
                  <div className="text-[10px] text-ink-faint mt-0.5">{n.time}</div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Settings */}
      <button className="w-8 h-8 rounded border border-border bg-white flex items-center justify-center text-ink-muted hover:bg-surface-muted">⚙</button>

      {/* Status */}
      <div className="flex items-center gap-1.5 px-3 py-1 rounded-full bg-green-50 border border-green-200 text-[11px] font-medium text-green-700">
        <span className="w-1.5 h-1.5 rounded-full bg-green-500 inline-block" />
        All systems normal
      </div>
    </header>
  )
}
