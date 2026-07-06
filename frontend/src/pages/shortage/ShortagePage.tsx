
import { toast } from 'sonner'
import { Badge } from '../../components/ui/Badge'
import { Button } from '../../components/ui/Button'
import { KPICard } from '../../components/ui/KPICard'
import type { Shortage } from '../../types'

const sevVariant = { emergency:'red', critical:'red', warning:'yellow' } as const
const sevLabel = { emergency:'Emergency', critical:'Critical', warning:'Warning' } as const

export function ShortagePage() {
  const shortages: Shortage[] = [
    { id: 'S1', medicine: 'Insulin', facility: 'City General', severity: 'emergency', stock: '12 units', daysLeft: 0, nearestSource: 'Apollo Hospital' },
    { id: 'S2', medicine: 'Oxygen', facility: 'Narayana Health', severity: 'critical', stock: '84 units', daysLeft: 2, nearestSource: 'Fortis BBT' },
    { id: 'S3', medicine: 'Amoxicillin', facility: 'Victoria Hospital', severity: 'warning', stock: '180 units', daysLeft: 6, nearestSource: 'Manipal Hospital' },
  ]

  function handleAction(_id: string, sev: string) {
    if (sev === 'emergency') {
      toast.success('Dispatching nearest donor — Emergency transfer initiated')
    } else if (sev === 'critical') {
      toast('Scanning donors within 5 km…', { icon:'🔍' })
      setTimeout(() => toast.success('Match found — 2 facilities within 5 km'), 1400)
    } else {
      toast('Review queued', { icon:'📋' })
    }
  }

  return (
    <div>
      <div className="grid grid-cols-4 gap-3 mb-4">
        <KPICard label="Emergency shortages" value={shortages.filter(s=>s.severity==='emergency').length} sub="Requires immediate action" trend="down" color="red" />
        <KPICard label="Critical shortages" value={shortages.filter(s=>s.severity==='critical').length} sub="Within 3 days of zero" trend="down" color="orange" />
        <KPICard label="Warnings" value={shortages.filter(s=>s.severity==='warning').length} sub="Monitor closely" color="orange" />
        <KPICard label="Resolved (7d)" value="41" sub="−12% vs last week" trend="up" color="green" />
      </div>

      <div className="panel">
        <div className="flex items-center justify-between mb-4">
          <div className="panel-title">Shortage intelligence feed</div>
          <Badge variant="red" pulse>Live</Badge>
        </div>
        <div className="overflow-x-auto">
          <table className="af-table">
            <thead>
              <tr><th>Medicine</th><th>Facility</th><th>Severity</th><th>Stock</th><th>Days left</th><th>Nearest source</th><th>Action</th></tr>
            </thead>
            <tbody>
              {shortages.map(s => (
                <tr key={s.id}>
                  <td><div className="font-medium">{s.medicine}</div></td>
                  <td className="text-ink-muted">{s.facility}</td>
                  <td><Badge variant={sevVariant[s.severity]}>{sevLabel[s.severity]}</Badge></td>
                  <td>{s.stock}</td>
                  <td style={{ color: s.daysLeft===0?'#dc2626':s.daysLeft<=3?'#ea580c':'#d97706', fontWeight:500 }}>
                    {s.daysLeft===0?'Now':s.daysLeft+' days'}
                  </td>
                  <td className="text-ink-muted">{s.nearestSource}</td>
                  <td>
                    <Button
                      variant={s.severity==='emergency'?'red':s.severity==='critical'?'orange':'ghost'}
                      size="sm"
                      onClick={() => handleAction(s.id, s.severity)}
                    >
                      {s.severity==='emergency'?'Dispatch':s.severity==='critical'?'Source':'Review'}
                    </Button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
