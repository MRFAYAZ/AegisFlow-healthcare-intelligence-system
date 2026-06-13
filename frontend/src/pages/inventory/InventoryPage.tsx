import { useState } from 'react'
import { toast } from 'sonner'
import { useAppStore } from '../../store/useAppStore'
import { Badge } from '../../components/ui/Badge'
import { Button } from '../../components/ui/Button'
import { Modal } from '../../components/ui/Modal'
import type { Medicine } from '../../types'
import { useInventory } from '../../hooks/useInventory'

const statusVariant: Record<Medicine['status'], 'red'|'orange'|'yellow'|'green'> = {
  emergency:'red', critical:'orange', warning:'yellow', adequate:'green'
}
const statusLabel: Record<Medicine['status'], string> = {
  emergency:'Emergency', critical:'Critical', warning:'Warning', adequate:'Adequate'
}
const barColor: Record<Medicine['status'], string> = {
  emergency:'#dc2626', critical:'#ea580c', warning:'#d97706', adequate:'#16a34a'
}

function AddItemModal({ onClose }: { onClose: () => void }) {
  const { addInventoryItem } = useAppStore()
  const [name, setName] = useState('')
  const [cat, setCat] = useState('Antibiotic')
  const [qty, setQty] = useState('100')
  const [expiry, setExpiry] = useState('')

  function submit() {
    if (!name.trim()) { toast.error('Please enter a medicine name'); return }
    addInventoryItem({
      id: `M${Date.now()}`, name, details: cat + ' · Added now',
      category: cat, stock: parseInt(qty)||0, maxStock: Math.max(parseInt(qty)*2, 100),
      expiry: expiry || 'N/A', status: 'adequate', unit: 'units'
    })
    toast.success(`${name} added to inventory`)
    onClose()
  }

  return (
    <Modal open title="Add inventory item" onClose={onClose}
      footer={<><Button variant="ghost" onClick={onClose}>Cancel</Button><Button variant="primary" onClick={submit}>Add item</Button></>}
    >
      <div className="mb-3"><label className="f-label">Medicine name</label><input className="f-input" value={name} onChange={e=>setName(e.target.value)} placeholder="e.g. Atorvastatin 20mg"/></div>
      <div className="mb-3"><label className="f-label">Category</label>
        <select className="f-input" value={cat} onChange={e=>setCat(e.target.value)}>
          {['Antibiotic','Analgesic','Endocrine','Emergency','Cardiac','Vitamin'].map(c=><option key={c}>{c}</option>)}
        </select>
      </div>
      <div className="mb-3"><label className="f-label">Quantity</label><input className="f-input" type="number" value={qty} onChange={e=>setQty(e.target.value)} min="1"/></div>
      <div><label className="f-label">Expiry</label><input className="f-input" type="month" value={expiry} onChange={e=>setExpiry(e.target.value)}/></div>
    </Modal>
  )
}

function RequestModal({ medicine, onClose }: { medicine: Medicine; onClose: () => void }) {
  const [type, setType] = useState('Emergency Transfer')
  const [qty, setQty] = useState('50')
  const [priority, setPriority] = useState('Emergency')
  const [notes, setNotes] = useState('')

  function submit() {
    toast.success(`${type} submitted — ${qty} units of ${medicine.name}`)
    onClose()
  }

  return (
    <Modal open title="Request restock" subtitle={`Restock request for ${medicine.name}`}
      onClose={onClose}
      footer={<><Button variant="ghost" onClick={onClose}>Cancel</Button><Button variant="primary" onClick={submit}>Submit request</Button></>}
    >
      <div className="mb-3"><label className="f-label">Medicine</label><input className="f-input" value={medicine.name} readOnly /></div>
      <div className="mb-3"><label className="f-label">Request type</label>
        <select className="f-input" value={type} onChange={e=>setType(e.target.value)}>
          {['Emergency Transfer','Standard Purchase Order','Inter-Hospital Transfer'].map(t=><option key={t}>{t}</option>)}
        </select>
      </div>
      <div className="mb-3"><label className="f-label">Quantity</label><input className="f-input" type="number" value={qty} onChange={e=>setQty(e.target.value)}/></div>
      <div className="mb-3"><label className="f-label">Priority</label>
        <select className="f-input" value={priority} onChange={e=>setPriority(e.target.value)}>
          {['Emergency','High','Normal'].map(p=><option key={p}>{p}</option>)}
        </select>
      </div>
      <div><label className="f-label">Notes</label><input className="f-input" value={notes} onChange={e=>setNotes(e.target.value)} placeholder="Additional context…"/></div>
    </Modal>
  )
}

export function InventoryPage() {
  const {data: inventory = [], isLoading} = useInventory()
  const [addOpen, setAddOpen] = useState(false)
  const [reqMed, setReqMed] = useState<Medicine|null>(null)
  const [search, setSearch] = useState('')
  const [filter, setFilter] = useState<'all'|'critical'|'warning'|'adequate'>('all')

  if (isLoading) {

  return (
    <div className="panel">
      Loading inventory...
    </div>
  )
}

  const filtered = inventory.filter(item => {
    const matchSearch = item.name.toLowerCase().includes(search.toLowerCase())
    const matchFilter = filter==='all' || item.status===filter || (filter==='critical' && (item.status==='critical'||item.status==='emergency'))
    return matchSearch && matchFilter
  })

  return (
    <div>
      <div className="panel">
        <div className="flex items-center justify-between mb-4">
          <div className="panel-title">Inventory register</div>
          <div className="flex gap-2">
            <input className="f-input" style={{width:160}} placeholder="Search medicines…" value={search} onChange={e=>setSearch(e.target.value)} />
            <select className="f-input" style={{width:130}} value={filter} onChange={e=>setFilter(e.target.value as typeof filter)}>
              <option value="all">All items</option>
              <option value="critical">Critical / Emergency</option>
              <option value="warning">Warning</option>
              <option value="adequate">Adequate</option>
            </select>
            <Button variant="primary" onClick={() => setAddOpen(true)}>+ Add item</Button>
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="af-table">
            <thead>
              <tr>
                <th>Medicine</th><th>Category</th><th>Stock</th>
                <th>Level</th><th>Expiry</th><th>Status</th><th>Action</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map(item => {
                const pct = Math.round((item.stock / item.maxStock) * 100)
                return (
                  <tr key={item.id}>
                    <td>
                      <div className="font-medium text-ink">{item.name}</div>
                      <div className="text-[10px] text-ink-faint">{item.details}</div>
                    </td>
                    <td className="text-ink-muted">{item.category}</td>
                    <td>{item.stock} {item.unit}</td>
                    <td>
                      <div className="progress-track" style={{ width:80 }}>
                        <div className="progress-fill" style={{ width:`${pct}%`, background: barColor[item.status] }} />
                      </div>
                    </td>
                    <td className="text-ink-muted">{item.expiry}</td>
                    <td><Badge variant={statusVariant[item.status]}>{statusLabel[item.status]}</Badge></td>
                    <td>
                      <Button
                        variant={item.status==='emergency'?'red':item.status==='adequate'?'ghost':'primary'}
                        size="sm"
                        onClick={() => item.status!=='adequate' && setReqMed(item)}
                      >
                        {item.status==='emergency'?'Urgent':item.status==='adequate'?'View':'Request'}
                      </Button>
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      </div>

      {addOpen && <AddItemModal onClose={() => setAddOpen(false)} />}
      {reqMed && <RequestModal medicine={reqMed} onClose={() => setReqMed(null)} />}
    </div>
  )
}
