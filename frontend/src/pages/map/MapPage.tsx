import { useState } from 'react'
import { Badge } from '../../components/ui/Badge'
import { mockFacilities } from '../../lib/mockData'
import type { Facility } from '../../types'

const statusColor: Record<Facility['status'], string> = {
  emergency:'#dc2626', critical:'#ea580c', low:'#d97706', stocked:'#16a34a'
}
const statusVariant: Record<Facility['status'], 'red'|'orange'|'yellow'|'green'> = {
  emergency:'red', critical:'orange', low:'yellow', stocked:'green'
}

export function MapPage() {
  const [selected, setSelected] = useState<Facility|null>(null)

  return (
    <div>
      <div className="grid grid-cols-3 gap-3">
        <div className="col-span-2 panel">
          <div className="flex items-center justify-between mb-3">
            <div className="panel-title">Geospatial intelligence — Bengaluru region</div>
            <Badge variant="blue">Leaflet.js integration point</Badge>
          </div>
          <div className="bg-[#ede9e3] border border-border rounded-lg overflow-hidden relative" style={{ height:480 }}>
            <svg width="100%" height="100%" viewBox="0 0 680 480" xmlns="http://www.w3.org/2000/svg">
              <rect width="680" height="480" fill="#ede9e3"/>
              <path d="M80,300 Q200,240 340,260 Q480,280 600,220" stroke="#c8c4bc" strokeWidth="2" fill="none"/>
              <path d="M100,180 Q240,160 340,200 Q440,240 580,200" stroke="#c8c4bc" strokeWidth="1.5" fill="none"/>
              <ellipse cx="340" cy="240" rx="220" ry="150" fill="rgba(37,99,235,0.03)" stroke="rgba(37,99,235,0.08)" strokeWidth="1" strokeDasharray="6,4"/>
              {mockFacilities.map(f => {
                const x = (f.lng - 77.55) * 3000 + 100
                const y = (12.99 - f.lat) * 3000 + 80
                const c = statusColor[f.status]
                const isSelected = selected?.id === f.id
                return (
                  <g key={f.id} onClick={() => setSelected(f)} style={{ cursor:'pointer' }}>
                    <circle cx={x} cy={y} r={isSelected?16:12} fill={c} fillOpacity={0.1} stroke={c} strokeWidth={isSelected?2:1.5}/>
                    <circle cx={x} cy={y} r={isSelected?6:4.5} fill={c}/>
                    <text x={x+14} y={y-3} fill={c} fontSize="8.5" fontWeight="600" fontFamily="-apple-system,sans-serif">{f.name.split(',')[0]}</text>
                    <text x={x+14} y={y+8} fill="#9a9890" fontSize="7.5" fontFamily="-apple-system,sans-serif">{f.status.toUpperCase()}</text>
                  </g>
                )
              })}
              {/* donor route lines */}
              <line x1="195" y1="222" x2="308" y2="262" stroke="rgba(22,163,74,0.4)" strokeWidth="1.5" strokeDasharray="5,3"/>
              <line x1="195" y1="222" x2="160" y2="318" stroke="rgba(37,99,235,0.35)" strokeWidth="1.5" strokeDasharray="5,3"/>
              <text x="12" y="470" fill="#9a9890" fontSize="7.5" fontFamily="-apple-system,sans-serif">Schematic · Replace with Leaflet.js + real tile layers + GeoJSON in production build</text>
            </svg>
            <div className="absolute bottom-3 left-3 bg-white border border-border rounded-lg p-2">
              {[['#dc2626','Emergency'],['#ea580c','Critical'],['#d97706','Warning'],['#16a34a','Stocked'],['#2563eb','Med shop']].map(([c,l])=>(
                <div key={l} className="flex items-center gap-1.5 text-[10px] text-ink-muted mb-1 last:mb-0">
                  <div className="w-2 h-2 rounded-full" style={{ background:c }}/>
                  {l}
                </div>
              ))}
            </div>
          </div>
        </div>

        <div className="flex flex-col gap-3">
          {/* Selected facility detail */}
          <div className="panel">
            <div className="panel-title mb-3">{selected ? selected.name : 'Facility detail'}</div>
            {selected ? (
              <div>
                <div className="mb-3"><Badge variant={statusVariant[selected.status]}>{selected.status.charAt(0).toUpperCase()+selected.status.slice(1)}</Badge></div>
                {[['Type', selected.type],['Address',selected.address],['Lat',selected.lat.toFixed(4)],['Lng',selected.lng.toFixed(4)]].map(([l,v])=>(
                  <div key={l} className="stat-row">
                    <span className="text-[12px] text-ink-muted">{l}</span>
                    <span className="text-[12px] text-ink font-medium capitalize">{String(v)}</span>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-[12px] text-ink-faint py-4 text-center">Click a facility on the map to view details</div>
            )}
          </div>

          {/* All facilities list */}
          <div className="panel flex-1">
            <div className="panel-title mb-3">All facilities ({mockFacilities.length})</div>
            {mockFacilities.map(f => (
              <div key={f.id}
                className={`flex items-center gap-2.5 py-2 border-b border-border last:border-b-0 cursor-pointer hover:bg-surface-muted rounded px-1 -mx-1 transition-colors ${selected?.id===f.id?'bg-blue-50':''}`}
                onClick={() => setSelected(f)}
              >
                <div className="w-2.5 h-2.5 rounded-full flex-shrink-0" style={{ background: statusColor[f.status] }} />
                <div className="flex-1 min-w-0">
                  <div className="text-[12px] font-medium text-ink truncate">{f.name}</div>
                  <div className="text-[10px] text-ink-faint">{f.address}</div>
                </div>
                <Badge variant={statusVariant[f.status]}>{f.status}</Badge>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
