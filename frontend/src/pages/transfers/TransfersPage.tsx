import { useState } from 'react'
import { toast } from 'sonner'
import { useTransfers } from '../../hooks/useTransfers'
import { Badge } from '../../components/ui/Badge'
import { Button } from '../../components/ui/Button'
import { Modal } from '../../components/ui/Modal'
import type { Transfer } from '../../types'
import { useAppStore } from '../../store/useAppStore'

const stVariant = { in_transit:'blue', pending:'yellow', delivered:'green', sourcing:'orange' } as const
const stLabel = { in_transit:'In transit', pending:'Pending', delivered:'Delivered', sourcing:'Sourcing' } as const

function TrackModal({ transfer, onClose }: { transfer: Transfer; onClose: () => void }) {
  const { updateTransferStatus } = useTransfers()
  function deliver() {
    updateTransferStatus(transfer.id, 'delivered', 'Done')
    toast.success(`${transfer.medicine} delivered to ${transfer.to}`)
    onClose()
  }
  return (
    <Modal open title="Transfer tracking" subtitle={transfer.id} onClose={onClose}
      footer={<><Button variant="ghost" onClick={onClose}>Close</Button><Button variant="green" onClick={deliver}>Mark delivered</Button></>}
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

function NewTransferModal({ onClose }: { onClose: () => void }) {
  const { addTransfer } = useAppStore()
  const [med, setMed] = useState('')
  const [from, setFrom] = useState('Fortis BBT')
  const [to, setTo] = useState('City General')
  const [qty, setQty] = useState('50')

  function submit() {
    if (!med.trim()) { toast.error('Please enter a medicine name'); return }
    const id = `#TF-${2850 + Math.floor(Math.random()*100)}`
    addTransfer({ id, medicine:med, from, to, quantity:`${qty} units`, status:'pending', eta:'—', createdAt: new Date().toISOString() })
    toast.success(`Transfer ${id} created — awaiting approval`)
    onClose()
  }

  const facilities = ['Fortis BBT','Manipal Hospital','Narayana Health',"St. John's",'Apollo KMG','City General','Jayanagar Regional','Victoria Hospital']

  return (
    <Modal open title="New transfer request" onClose={onClose}
      footer={<><Button variant="ghost" onClick={onClose}>Cancel</Button><Button variant="primary" onClick={submit}>Create transfer</Button></>}
    >
      <div className="mb-3"><label className="f-label">Medicine</label><input className="f-input" value={med} onChange={e=>setMed(e.target.value)} placeholder="e.g. Insulin Glargine"/></div>
      <div className="mb-3"><label className="f-label">From facility</label>
        <select className="f-input" value={from} onChange={e=>setFrom(e.target.value)}>{facilities.map(f=><option key={f}>{f}</option>)}</select>
      </div>
      <div className="mb-3"><label className="f-label">To facility</label>
        <select className="f-input" value={to} onChange={e=>setTo(e.target.value)}>{facilities.map(f=><option key={f}>{f}</option>)}</select>
      </div>
      <div><label className="f-label">Quantity</label><input className="f-input" type="number" value={qty} onChange={e=>setQty(e.target.value)} min="1"/></div>
    </Modal>
  )
}

export function TransfersPage() {
  const { data: transfers = [], updateTransferStatus } = useTransfers()
  const [trackTf, setTrackTf] = useState<Transfer|null>(null)
  const [newOpen, setNewOpen] = useState(false)

  function approve(id: string) {
    updateTransferStatus(id, 'in_transit', '~35 min')
    toast.success(`Transfer ${id} approved and dispatched`)
  }

  return (
    <div>
      <div className="panel">
        <div className="flex items-center justify-between mb-4">
          <div className="panel-title">Transfer center</div>
          <Button variant="primary" onClick={() => setNewOpen(true)}>+ New transfer</Button>
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
                    {t.status==='pending' && <Button variant="primary" size="sm" onClick={() => approve(t.id)}>Approve</Button>}
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
      {newOpen && <NewTransferModal onClose={() => setNewOpen(false)} />}
    </div>
  )
}
