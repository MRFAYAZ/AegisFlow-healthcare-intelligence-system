import { useState } from 'react'
import { toast } from 'sonner'
import { useAppStore } from '../../store/useAppStore'
import { Badge } from '../../components/ui/Badge'
import { Button } from '../../components/ui/Button'
import { Modal } from '../../components/ui/Modal'
import type { Emergency } from '../../types'

const donors = [
  { name:'Fortis Hospital, Bannerghatta', units:24, distance:'2.1 km', eta:'22 min', type:'hospital' },
  { name:'MedPlus, JP Nagar', units:11, distance:'3.4 km', eta:'30 min', type:'pharmacy' },
  { name:'Narayana Health, Rajajinagar', units:6, distance:'5.8 km', eta:'45 min', type:'hospital' },
]

function ActivateModal({ emergency, onClose }: { emergency: Emergency; onClose: () => void }) {
  const [step, setStep] = useState(1)
  const [qty, setQty] = useState('10')
  const [note, setNote] = useState('')
  const { updateEmergencyStatus } = useAppStore()

  function next() {
    if (step === 2) {
      updateEmergencyStatus(emergency.id, 'in_transit')
      toast.success(`Dispatch activated — Transfer #TF-${Date.now().toString().slice(-4)} created`)
      setStep(3)
    } else if (step === 3) {
      onClose()
    } else {
      setStep(s => s + 1)
    }
  }

  const stepLabels = ['Review incident', 'Select donor', 'Confirmed']

  return (
    <Modal
      open title="Activate Emergency Dispatch"
      subtitle={`${emergency.medicine} — ${emergency.facility}`}
      onClose={onClose}
      footer={
        <>
          {step > 1 && step < 3 && <Button variant="ghost" onClick={() => setStep(s=>s-1)}>Back</Button>}
          <Button variant="ghost" onClick={onClose}>Cancel</Button>
          <Button variant={step===3?'green':step===2?'orange':'red'} onClick={next}>
            {step===1?'Review donor →':step===2?'Confirm dispatch →':'Done'}
          </Button>
        </>
      }
    >
      {/* Steps */}
      <div className="flex gap-1.5 mb-1">
        {[1,2,3].map(s => (
          <div key={s} className="flex-1 h-1 rounded"
            style={{ background: s<step ? '#16a34a' : s===step ? '#2563eb' : '#e5e3de' }} />
        ))}
      </div>
      <div className="text-[10px] text-ink-faint mb-4">Step {step} of 3 — {stepLabels[step-1]}</div>

      {step === 1 && (
        <div>
          <div className="bg-red-50 border border-red-200 rounded-lg p-3 mb-4">
            <div className="text-[12px] font-semibold text-red-800 mb-1">Zero stock — patients at risk</div>
            <div className="text-[11px] text-red-700">Immediate redistribution required from nearest donor facility.</div>
          </div>
          {[['Medicine', emergency.medicine],['Requesting facility', emergency.facility],['Units on hand', `${emergency.units} units`],['Priority','—']].map(([l,v]) => (
            <div key={l} className="flex justify-between items-center py-2 border-b border-border last:border-b-0">
              <span className="text-[12px] text-ink-muted">{l}</span>
              <span className={`text-[12px] font-medium ${l==='Priority'?'':'text-ink'}`}>
                {l==='Priority' ? <Badge variant="red">Emergency</Badge> : v}
              </span>
            </div>
          ))}
        </div>
      )}

      {step === 2 && (
        <div>
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-3 mb-3 text-[12px] text-blue-800">
            AI matched donor <strong>{emergency.donor}</strong> — {emergency.donorUnits} units available, {emergency.distance} away. ETA: {emergency.eta}.
          </div>
          <div className="bg-surface-muted border border-border rounded-lg p-3 mb-3 flex items-center gap-3">
            <div className="w-8 h-8 rounded bg-blue-50 border border-blue-200 flex items-center justify-center text-sm flex-shrink-0">🏥</div>
            <div className="flex-1">
              <div className="text-[12px] font-medium text-ink">{emergency.donor}</div>
              <div className="text-[11px] text-ink-faint">{emergency.donorUnits} units · {emergency.distance} · ETA {emergency.eta}</div>
            </div>
            <Badge variant="green">Best match</Badge>
          </div>
          <div className="mb-3">
            <label className="f-label">Dispatch quantity</label>
            <input className="f-input" type="number" value={qty} onChange={e=>setQty(e.target.value)} min="1" max={emergency.donorUnits} />
          </div>
          <div>
            <label className="f-label">Urgency note (optional)</label>
            <input className="f-input" value={note} onChange={e=>setNote(e.target.value)} placeholder="e.g. ICU patient requires immediate dose" />
          </div>
        </div>
      )}

      {step === 3 && (
        <div className="text-center py-4">
          <div className="w-12 h-12 rounded-full bg-green-50 border-2 border-green-200 flex items-center justify-center mx-auto mb-3">
            <span className="text-green-600 text-xl">✓</span>
          </div>
          <div className="text-[15px] font-semibold text-green-700 mb-1">Dispatch Activated</div>
          <div className="text-[12px] text-ink-faint mb-4">Donor facility has been notified. Transfer is now in progress.</div>
          {[['Status','In transit'],['Donor', emergency.donor],['ETA', emergency.eta]].map(([l,v]) => (
            <div key={l} className="flex justify-between items-center py-2 border-b border-border last:border-b-0">
              <span className="text-[12px] text-ink-muted">{l}</span>
              <span className="text-[12px] font-medium">{l==='Status'?<Badge variant="blue">In transit</Badge>:v}</span>
            </div>
          ))}
        </div>
      )}
    </Modal>
  )
}

function TrackModal({ emergency, onClose }: { emergency: Emergency; onClose: () => void }) {
  const { updateEmergencyStatus } = useAppStore()
  function markDelivered() {
    updateEmergencyStatus(emergency.id, 'resolved')
    toast.success(`${emergency.medicine} delivered to ${emergency.facility}`)
    onClose()
  }
  return (
    <Modal open title="Transfer in Progress" subtitle={emergency.medicine}
      onClose={onClose}
      footer={<><Button variant="ghost" onClick={onClose}>Close</Button><Button variant="green" onClick={markDelivered}>Mark delivered</Button></>}
    >
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-3 mb-4 text-[12px] text-blue-800">
        Transfer in progress from <strong>{emergency.donor}</strong> to <strong>{emergency.facility}</strong>.
      </div>
      {[['Medicine',emergency.medicine],['From',emergency.donor],['To',emergency.facility],['ETA',emergency.eta],['Status','In transit']].map(([l,v])=>(
        <div key={l} className="flex justify-between items-center py-2 border-b border-border last:border-b-0">
          <span className="text-[12px] text-ink-muted">{l}</span>
          <span className="text-[12px] font-medium">{l==='Status'?<Badge variant="blue">In transit</Badge>:v}</span>
        </div>
      ))}
    </Modal>
  )
}

function SourceModal({ emergency, onClose }: { emergency: Emergency; onClose: () => void }) {
  const { updateEmergencyStatus } = useAppStore()
  function confirm() {
    updateEmergencyStatus(emergency.id, 'in_transit')
    toast.success(`Sourcing confirmed — transfer initiated to ${emergency.facility}`)
    onClose()
  }
  return (
    <Modal open title="Source Medicine" subtitle={`${emergency.medicine} — ${emergency.facility}`}
      onClose={onClose}
      footer={<><Button variant="ghost" onClick={onClose}>Cancel</Button><Button variant="orange" onClick={confirm}>Dispatch to nearest</Button></>}
    >
      <div className="bg-orange-50 border border-orange-200 rounded-lg p-3 mb-3 text-[12px] text-orange-800">
        Scanning all facilities within 10 km for <strong>{emergency.medicine}</strong>.
      </div>
      <div className="bg-surface-muted border border-border rounded-lg p-3 mb-3 flex items-center gap-3">
        <div className="w-8 h-8 rounded bg-blue-50 border border-blue-200 flex items-center justify-center text-sm flex-shrink-0">🏥</div>
        <div className="flex-1">
          <div className="text-[12px] font-medium text-ink">{emergency.donor}</div>
          <div className="text-[11px] text-ink-faint">{emergency.donorUnits} units · {emergency.distance} · ETA {emergency.eta}</div>
        </div>
        <Badge variant="green">Best match</Badge>
      </div>
      {[['Units to request','20 units'],['Recipient',emergency.facility]].map(([l,v])=>(
        <div key={l} className="flex justify-between py-2 border-b border-border last:border-b-0">
          <span className="text-[12px] text-ink-muted">{l}</span>
          <span className="text-[12px] font-medium text-ink">{v}</span>
        </div>
      ))}
    </Modal>
  )
}

export function EmergencyPage() {
  const { emergencies } = useAppStore()
  const [activateModal, setActivateModal] = useState<Emergency|null>(null)
  const [trackModal, setTrackModal] = useState<Emergency|null>(null)
  const [sourceModal, setSourceModal] = useState<Emergency|null>(null)

  const active = emergencies.filter(e => e.status !== 'resolved')

  function handleAction(e: Emergency) {
    if (e.status === 'pending') setActivateModal(e)
    else if (e.status === 'in_transit') setTrackModal(e)
    else if (e.status === 'sourcing') setSourceModal(e)
  }

  const statusBadge = (s: Emergency['status']) => {
    if (s==='pending') return <Badge variant="red">Awaiting</Badge>
    if (s==='in_transit') return <Badge variant="blue">In transit</Badge>
    if (s==='sourcing') return <Badge variant="orange">Sourcing</Badge>
    return <Badge variant="green">Resolved</Badge>
  }
  const btnVariant = (s: Emergency['status']) => s==='pending'?'red':s==='in_transit'?'primary':'orange' as const
  const btnLabel = (s: Emergency['status']) => s==='pending'?'Activate':s==='in_transit'?'Track':'Source'

  return (
    <div>
      {/* Banner */}
      <div className="emer-banner">
        <div className="w-7 h-7 rounded bg-red-200 flex items-center justify-center text-status-red font-bold flex-shrink-0">!</div>
        <div className="flex-1">
          <div className="text-[13px] font-semibold text-red-800">Emergency Operations — {active.length} active incident{active.length!==1?'s':''}</div>
          <div className="text-[11px] text-red-700">AI redistribution engine active · Real-time donor matching</div>
        </div>
        <Badge variant="red" pulse>● Live</Badge>
      </div>

      <div className="grid grid-cols-2 gap-4">
        {/* Left col */}
        <div>
          <div className="panel mb-3">
            <div className="flex items-center justify-between mb-3">
              <div className="panel-title">Active incidents</div>
              <div className="text-[11px] text-ink-faint">{active.length} active</div>
            </div>
            {active.length === 0 ? (
              <div className="text-center py-6 text-ink-faint text-[12px]">
                <div className="text-2xl mb-2">✓</div>No active emergencies
              </div>
            ) : (
              active.map(e => (
                <div key={e.id} className="alert-row items-start">
                  <div className="alert-dot mt-1.5" style={{ background: e.severity==='emergency'?'#dc2626':'#ea580c' }} />
                  <div className="flex-1 min-w-0">
                    <div className="text-[12px] font-medium text-ink">{e.medicine}</div>
                    <div className="text-[11px] text-ink-faint">{e.facility}</div>
                    <div className="text-[11px] text-ink-faint mt-0.5">{e.units} units · Nearest: {e.donor} ({e.distance})</div>
                    <div className="mt-1.5">{statusBadge(e.status)}</div>
                  </div>
                  <Button variant={btnVariant(e.status)} size="sm" onClick={() => handleAction(e)}>
                    {btnLabel(e.status)}
                  </Button>
                </div>
              ))
            )}
          </div>

          <div className="panel">
            <div className="panel-title mb-3">Nearest donors — Epinephrine</div>
            {donors.map(d => (
              <div key={d.name} className="stat-row">
                <div className="flex items-center gap-2 text-[12px] text-ink">
                  <span>{d.type==='hospital'?'🏥':'🏪'}</span>
                  <span>{d.name}</span>
                </div>
                <div className="flex items-center gap-2">
                  <Badge variant="green">{d.units} units</Badge>
                  <span className="text-[10px] text-ink-faint">{d.distance}</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Map */}
        <div className="panel">
          <div className="panel-title mb-3">Live map — Bengaluru</div>
          <div className="bg-[#f0eeea] border border-border rounded-lg overflow-hidden relative" style={{ height:400 }}>
            <svg width="100%" height="100%" viewBox="0 0 400 400" xmlns="http://www.w3.org/2000/svg">
              <rect width="400" height="400" fill="#ede9e3"/>
              <line x1="0" y1="200" x2="400" y2="200" stroke="#d8d5cf" strokeWidth="1"/>
              <line x1="200" y1="0" x2="200" y2="400" stroke="#d8d5cf" strokeWidth="1"/>
              <path d="M80,280 Q160,220 200,200 Q240,180 310,160" stroke="#b8b4ac" strokeWidth="2" fill="none" strokeLinecap="round"/>
              {/* Emergency */}
              <circle cx="170" cy="210" r="28" fill="rgba(220,38,38,0.08)" stroke="rgba(220,38,38,0.2)" strokeWidth="1" strokeDasharray="4,3"/>
              <circle cx="170" cy="210" r="10" fill="#fef2f2" stroke="#dc2626" strokeWidth="1.5"/>
              <circle cx="170" cy="210" r="4.5" fill="#dc2626"/>
              <text x="186" y="206" fill="#991b1b" fontSize="8.5" fontWeight="600" fontFamily="-apple-system,sans-serif">City General</text>
              <text x="186" y="217" fill="#b91c1c" fontSize="7.5" fontFamily="-apple-system,sans-serif">EMERGENCY</text>
              {/* Critical */}
              <circle cx="260" cy="158" r="9" fill="#fff7ed" stroke="#ea580c" strokeWidth="1.5"/>
              <circle cx="260" cy="158" r="4" fill="#ea580c"/>
              <text x="274" y="153" fill="#c2410c" fontSize="8.5" fontWeight="600" fontFamily="-apple-system,sans-serif">Apollo KMG</text>
              <text x="274" y="164" fill="#ea580c" fontSize="7.5" fontFamily="-apple-system,sans-serif">CRITICAL</text>
              {/* Donors */}
              <circle cx="118" cy="128" r="7" fill="#f0fdf4" stroke="#16a34a" strokeWidth="1.5"/>
              <circle cx="118" cy="128" r="3.5" fill="#16a34a"/>
              <text x="130" y="132" fill="#166534" fontSize="8" fontFamily="-apple-system,sans-serif">Fortis BBT</text>
              <circle cx="310" cy="268" r="7" fill="#f0fdf4" stroke="#16a34a" strokeWidth="1.5"/>
              <circle cx="310" cy="268" r="3.5" fill="#16a34a"/>
              <text x="320" y="272" fill="#166534" fontSize="8" fontFamily="-apple-system,sans-serif">Narayana</text>
              <circle cx="82" cy="268" r="7" fill="#eff6ff" stroke="#2563eb" strokeWidth="1.5"/>
              <circle cx="82" cy="268" r="3.5" fill="#2563eb"/>
              <text x="94" y="272" fill="#1e40af" fontSize="8" fontFamily="-apple-system,sans-serif">MedPlus</text>
              {/* Routes */}
              <line x1="170" y1="210" x2="118" y2="128" stroke="rgba(22,163,74,0.5)" strokeWidth="1.5" strokeDasharray="5,3"/>
              <line x1="170" y1="210" x2="82" y2="268" stroke="rgba(37,99,235,0.4)" strokeWidth="1.5" strokeDasharray="5,3"/>
              <text x="10" y="390" fill="#9a9890" fontSize="7.5" fontFamily="-apple-system,sans-serif">Schematic · Leaflet.js + GeoJSON in production</text>
            </svg>
            <div className="absolute bottom-2.5 left-2.5 bg-white border border-border rounded-lg p-2">
              {[['#dc2626','Emergency'],['#ea580c','Critical'],['#16a34a','Donor'],['#2563eb','Med shop']].map(([c,l])=>(
                <div key={l} className="flex items-center gap-1.5 text-[10px] text-ink-muted mb-1 last:mb-0">
                  <div className="w-2 h-2 rounded-full" style={{ background:c }}/>
                  {l}
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {activateModal && <ActivateModal emergency={activateModal} onClose={() => setActivateModal(null)} />}
      {trackModal && <TrackModal emergency={trackModal} onClose={() => setTrackModal(null)} />}
      {sourceModal && <SourceModal emergency={sourceModal} onClose={() => setSourceModal(null)} />}
    </div>
  )
}
