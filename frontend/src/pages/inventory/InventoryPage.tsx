import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Badge } from '../../components/ui/Badge'
import { Button } from '../../components/ui/Button'
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

export function InventoryPage() {
  const {data: inventory = [], isLoading } = useInventory()
  const [search, setSearch] = useState('')
  const [filter, setFilter] = useState<'all'|'critical'|'warning'|'adequate'>('all')
  const navigate = useNavigate()

  if (isLoading) {
    return (
      <div className="panel">
        Loading inventory...
      </div>
    )
  }

  const transformedInventory: Medicine[] = inventory.map((item: any) => ({ id: item.inventory_id, name: item.medicine_name || item.medicine_id, 
  details: `Facility: ${  item.facility_name || item.facility_id }`, category: item.category || 'Medicine', stock: item.available_stock, maxStock: item.total_stock, expiry: 'N/A', unit: 'Units', status: item.severity === 'SAFE' ? 'adequate' : item.severity === 'WARNING' ? 'warning' : item.severity === 'CRITICAL' ? 'critical' : 'emergency' }))

  const filtered = transformedInventory.filter(item => {
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
            <span className="text-[11px] text-ink-faint">Live backend inventory</span>
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
                const pct = item.maxStock > 0 ? Math.round((item.stock / item.maxStock) * 100) : 0
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
                        onClick={() => navigate('/shortage')}
                      >
                        {item.status==='emergency'?'Open emergency':item.status==='adequate'?'View risk':'Review shortage'}
                      </Button>
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      </div>

    </div>
  )
}
