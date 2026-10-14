import { useState } from 'react'
import { toast } from 'sonner'
import { useTransfers } from '../../hooks/useTransfers'
import { Badge } from '../../components/ui/Badge'
import { Button } from '../../components/ui/Button'
import { Modal } from '../../components/ui/Modal'
import type { Transfer } from '../../types'

const stVariant = { in_transit:'blue', pending:'yellow', delivered:'green', sourcing:'orange' } as const
const stLabel = { in_transit:'In transit', pending:'Pending', delivered:'Delivered', sourcing:'Sourcing' } as const

function TrackModal({ transfer, onClose }: { transfer: Transfer; onClose: () => void }) {
  return (
    <Modal open title="Transfer tracking" subtitle={transfer.id} onClose={onClose}
      footer={<Button variant="ghost" onClick={onClose}>Close</Button>}
    >
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-3 mb-4 text-[12px] text-blue-800">
        Transfer in transit — ETA: <strong>{transfer.eta}</strong>
      </div>
      {[['Medicine',transfer.medicine],['From',transfer.from],['To',transfer.to],['Quantity',transfer.quantity],['Status','In transit'],['ETA',transfer.eta]].map(([l,v])=>(
        <div key={l} className="flex justify-between py-2 border-b border-border last:border-b-0">
          <span className="text-[12px] text-ink-muted">{l}</span>
          <span className="text-[12px] font-medium">{l==='Status'?<Badge variant="blue">In transit</Badge>:v}</span>
        </div>
      ))}
    </Modal>
  )
}

export function TransfersPage() {
  const { data: transfers = [], approveTransfer, isApproving } = useTransfers()
  const [trackTf, setTrackTf] = useState<Transfer|null>(null)

  async function approve(transfer: Transfer) {
    try {
      await approveTransfer(transfer.id, Number.parseInt(transfer.quantity, 10))
      toast.success(`Transfer ${transfer.id} approved`)
    } catch {
      toast.error('Approval failed. The transfer was not changed.')
    }
  }

  return (
    <div>
      <div className="panel">
        <div className="flex items-center justify-between mb-4">
          <div className="panel-title">Transfer center</div>
          <span className="text-[11px] text-ink-faint">Requests originate from emergency allocation</span>
        </div>
        <div className="overflow-x-auto">
          <table className="af-table">
            <thead>
              <tr><th>Transfer ID</th><th>Medicine</th><th>From</th><th>To</th><th>Qty</th><th>Status</th><th>ETA</th><th>Action</th></tr>
            </thead>
            <tbody>
              {transfers.map(t => (
                <tr key={t.id}>
                  <td className="text-blue-600 font-medium">{t.id}</td>
                  <td>{t.medicine}</td>
                  <td className="text-ink-muted">{t.from}</td>
                  <td className="text-ink-muted">{t.to}</td>
                  <td>{t.quantity}</td>
                  <td><Badge variant={stVariant[t.status]}>{stLabel[t.status]}</Badge></td>
                  <td className="text-ink-muted">{t.eta}</td>
                  <td>
                    {t.status==='pending' && <Button variant="primary" size="sm" disabled={isApproving} onClick={() => approve(t)}>Approve</Button>}
                    {t.status==='in_transit' && <Button variant="ghost" size="sm" onClick={() => setTrackTf(t)}>Track</Button>}
                    {(t.status==='delivered'||t.status==='sourcing') && <Button variant="ghost" size="sm" className="opacity-40" disabled>Done</Button>}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
      {trackTf && <TrackModal transfer={trackTf} onClose={() => setTrackTf(null)} />}
    </div>
  )
}
