import { useState } from 'react'
import { toast } from 'sonner'
import { KPICard } from '../../components/ui/KPICard'
import { Badge } from '../../components/ui/Badge'
import { Button } from '../../components/ui/Button'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'

const expiryItems = [
  { name:'Atorvastatin 20mg', qty:'48 strips', exp:'Jan 15, 2025', days:14, severity:'red' as const },
  { name:'Vitamin D3 60K', qty:'120 capsules', exp:'Feb 3, 2025', days:33, severity:'orange' as const },
  { name:'Metformin XR', qty:'200 strips', exp:'Feb 28, 2025', days:58, severity:'yellow' as const },
  { name:'Cetirizine 10mg', qty:'300 strips', exp:'Mar 20, 2025', days:78, severity:'yellow' as const },
]

const topDemand = [
  { name:'Paracetamol 500mg', units:842 },{ name:'Cetirizine 10mg', units:612 },
  { name:'Amoxicillin 500mg', units:540 },{ name:'Azithromycin 500mg', units:410 },
  { name:'Vitamin C 500mg', units:380 },
]

export function ShopPage() {
  const [entries, setEntries] = useState([
    { id:1, med:'Paracetamol 500mg', qty:100, supplier:'Apollo Pharmacy', date:'2024-01-15', status:'received' },
    { id:2, med:'Cetirizine 10mg', qty:200, supplier:'MedLine Dist.', date:'2024-01-14', status:'pending' },
  ])
  const [showAdd, setShowAdd] = useState(false)
  const [newMed, setNewMed] = useState(''); const [newQty, setNewQty] = useState('50'); const [newSup, setNewSup] = useState('')

  function addPurchase() {
    if (!newMed.trim()) { toast.error('Enter medicine name'); return }
    setEntries(prev => [{ id: Date.now(), med:newMed, qty:parseInt(newQty), supplier:newSup||'Unknown', date:new Date().toISOString().split('T')[0], status:'pending' }, ...prev])
    toast.success(`Purchase entry added for ${newMed}`)
    setShowAdd(false); setNewMed(''); setNewQty('50'); setNewSup('')
  }

  return (
    <div>
      <div className="grid grid-cols-4 gap-3 mb-4">
        <KPICard label="Total SKUs" value="1,842" sub="+24 this month" trend="up" color="blue" />
        <KPICard label="Low stock items" value="34" sub="Needs reorder" trend="down" color="orange" />
        <KPICard label="Expiring in 30d" value="12" sub="Immediate action needed" trend="down" color="red" />
        <KPICard label="Today's sales" value="₹42,310" sub="+8% vs yesterday" trend="up" color="green" />
      </div>

      <div className="grid grid-cols-2 gap-3 mb-3">
        <div className="panel">
          <div className="panel-title mb-3">Expiry monitor</div>
          {expiryItems.map(item => (
            <div key={item.name} className="alert-row">
              <div className="alert-dot" style={{ background: item.severity==='red'?'#dc2626':item.severity==='orange'?'#ea580c':'#d97706' }} />
              <div className="flex-1">
                <div className="text-[12px] font-medium text-ink">{item.name}</div>
                <div className="text-[11px] text-ink-faint">{item.qty} · Exp: {item.exp}</div>
              </div>
              <div className="text-[11px] font-medium" style={{ color: item.severity==='red'?'#dc2626':item.severity==='orange'?'#ea580c':'#d97706' }}>
                {item.days}d
              </div>
            </div>
          ))}
        </div>

        <div className="panel">
          <div className="panel-title mb-3">Top demand this week</div>
          <ResponsiveContainer width="100%" height={180}>
            <BarChart data={topDemand} layout="vertical" barSize={12}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e5e3de" horizontal={false}/>
              <XAxis type="number" tick={{ fontSize:10, fill:'#9a9890' }} axisLine={false} tickLine={false}/>
              <YAxis dataKey="name" type="category" tick={{ fontSize:10, fill:'#6b6860' }} axisLine={false} tickLine={false} width={100}/>
              <Tooltip contentStyle={{ fontSize:12, borderRadius:8, border:'1px solid #e5e3de' }}/>
              <Bar dataKey="units" fill="#2563eb" radius={[0,4,4,0]}/>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Purchase entries */}
      <div className="panel">
        <div className="flex items-center justify-between mb-4">
          <div className="panel-title">Purchase entries</div>
          <Button variant="primary" onClick={() => setShowAdd(p=>!p)}>+ Add entry</Button>
        </div>

        {showAdd && (
          <div className="bg-surface-muted border border-border rounded-lg p-3 mb-4 grid grid-cols-4 gap-3 items-end">
            <div><label className="f-label">Medicine</label><input className="f-input" value={newMed} onChange={e=>setNewMed(e.target.value)} placeholder="Medicine name"/></div>
            <div><label className="f-label">Quantity</label><input className="f-input" type="number" value={newQty} onChange={e=>setNewQty(e.target.value)}/></div>
            <div><label className="f-label">Supplier</label><input className="f-input" value={newSup} onChange={e=>setNewSup(e.target.value)} placeholder="Supplier name"/></div>
            <div className="flex gap-2"><Button variant="primary" onClick={addPurchase}>Add</Button><Button variant="ghost" onClick={()=>setShowAdd(false)}>Cancel</Button></div>
          </div>
        )}

        <table className="af-table">
          <thead><tr><th>Medicine</th><th>Quantity</th><th>Supplier</th><th>Date</th><th>Status</th></tr></thead>
          <tbody>
            {entries.map(e => (
              <tr key={e.id}>
                <td className="font-medium">{e.med}</td>
                <td>{e.qty} units</td>
                <td className="text-ink-muted">{e.supplier}</td>
                <td className="text-ink-muted">{e.date}</td>
                <td><Badge variant={e.status==='received'?'green':'yellow'}>{e.status==='received'?'Received':'Pending'}</Badge></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
