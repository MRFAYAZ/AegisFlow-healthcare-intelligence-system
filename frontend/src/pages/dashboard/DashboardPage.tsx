import { useNavigate } from 'react-router-dom'
import { KPICard } from '../../components/ui/KPICard'
import { EmergencyBanner } from '../../components/ui/EmergencyBanner'
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend } from 'recharts'
import { useDashboard } from '../../hooks/useDashboard'

export function DashboardPage() {
  const { data, isLoading } = useDashboard()
  const navigate = useNavigate()

  const severityData = [
    { name: 'Safe', value: Number(data?.safe_inventory ?? 0), fill: '#16a34a' },
    { name: 'Warning', value: Number(data?.warning_inventory ?? 0), fill: '#d97706' },
    { name: 'Critical', value: Number(data?.critical_inventory ?? 0), fill: '#ea580c' },
    { name: 'Emergency', value: Number(data?.emergency_inventory ?? 0), fill: '#dc2626' },
  ]

  const totalInventory = Number(data?.safe_inventory ?? 0) + Number(data?.warning_inventory ?? 0) + Number(data?.critical_inventory ?? 0) + Number(data?.emergency_inventory ?? 0)
  
  // Calculate health score percentage safely
  const healthScore = totalInventory > 0 ? Math.round((Number(data?.safe_inventory ?? 0) / totalInventory) * 100) : 0

  // Determine status color based on emergencies and critical inventory
  const requiresAttention = (Number(data?.active_emergencies ?? 0)) > 0 || (Number(data?.critical_inventory ?? 0)) > 0

  if (isLoading) {
    return (
      <div className="panel">
        <div className="animate-pulse text-ink-faint">Loading dashboard...</div>
      </div>
    )
  }

  return (
    <div className="space-y-6 p-6 bg-gray-50 min-h-screen">
      <div className="mb-8">
      </div>
      
      <EmergencyBanner count={Number(data?.active_emergencies ?? 0)} onView={() => navigate('/emergency')} />

      {/* KPIs Row */}
      <div className="grid grid-cols-4 gap-4">
        <KPICard label="Facilities" value={Number(data?.facilities ?? 0)} sub="Registered Facilities" color="blue" />
        <KPICard label="Medicines" value={Number(data?.medicines ?? 0)} sub="Tracked medicines" color="green" />
        <KPICard label="Critical Inventory" value={Number(data?.critical_inventory ?? 0) + Number(data?.emergency_inventory ?? 0)} sub="Requires action" color="red" />
        <KPICard label="Transfers" value={Number(data?.total_transfers ?? 0)} sub="Redistribution requests" color="orange" />
      </div>

      {/* Row 1: Visual Distribution & Health */}
      <div className="grid grid-cols-3 gap-4">
        <div className="col-span-2 panel shadow-md border border-border">
          <div className="panel-title mb-4">Inventory Distribution</div>
          <div className="bg-white p-4 rounded-lg flex flex-col items-center">
            <ResponsiveContainer width="100%" height={320}>
              <PieChart>
                <Pie 
                  data={severityData} 
                  dataKey="value" 
                  nameKey="name" 
                  cx="50%" 
                  cy="50%" 
                  innerRadius={80}
                  outerRadius={110} 
                  paddingAngle={2}
                  label={({ name, value }) => `${name}: ${value}`}
                  labelLine={true}
                >
                  {severityData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.fill} />
                  ))}
                </Pie>
                <Tooltip 
                  contentStyle={{ borderRadius: 8, border: '1px solid #e5e3de' }}
                  formatter={(value) => [`${value} items`, 'Count']}
                />
                <Legend verticalAlign="bottom" height={36}/>
              </PieChart>
            </ResponsiveContainer>
            <div className="mt-4 text-sm text-ink-faint">
              Total Inventory: <strong className="text-ink">{totalInventory}</strong>
            </div>
          </div>
        </div>

        <div className="panel shadow-md border border-border flex flex-col">
          <div className="panel-title mb-5">Inventory Health Score</div>
          <div className="flex-1 flex flex-col justify-center items-center mb-6">
            <div className={`text-6xl font-bold mb-2 ${healthScore > 80 ? 'text-green-600' : 'text-orange-500'}`}>
              {healthScore}%
            </div>
            <div className="text-sm text-ink-faint">Overall System Health</div>
          </div>
          <div className="space-y-3 mt-auto">
            <div className="flex justify-between items-center p-2 rounded bg-green-50">
              <div className="flex items-center gap-2"><span className="w-3 h-3 rounded-full bg-green-600" /><span className="text-sm text-ink">Safe</span></div>
              <strong className="text-green-600">{Number(data?.safe_inventory ?? 0)}</strong>
            </div>
            <div className="flex justify-between items-center p-2 rounded bg-yellow-50">
              <div className="flex items-center gap-2"><span className="w-3 h-3 rounded-full bg-yellow-600" /><span className="text-sm text-ink">Warning</span></div>
              <strong className="text-yellow-600">{Number(data?.warning_inventory ?? 0)}</strong>
            </div>
            <div className="flex justify-between items-center p-2 rounded bg-orange-50">
              <div className="flex items-center gap-2"><span className="w-3 h-3 rounded-full bg-orange-600" /><span className="text-sm text-ink">Critical</span></div>
              <strong className="text-orange-600">{Number(data?.critical_inventory ?? 0)}</strong>
            </div>
            <div className="flex justify-between items-center p-2 rounded bg-red-50">
              <div className="flex items-center gap-2"><span className="w-3 h-3 rounded-full bg-red-600" /><span className="text-sm text-ink">Emergency</span></div>
              <strong className="text-red-600">{Number(data?.emergency_inventory ?? 0)}</strong>
            </div>
          </div>
        </div>
      </div>

      {/* Row 2: Operational Overviews */}
      <div className="grid grid-cols-3 gap-4">
        {/* Emergency Monitor */}
        <div className="panel shadow-md border border-border flex flex-col h-full">
          <div className="panel-title mb-5">Emergency Monitor</div>
          <div className="space-y-4 flex-1 flex flex-col justify-between">
            <div>
              <div className="flex justify-between items-center pb-2 border-b border-gray-100">
                <span className="text-sm text-ink">Active Emergencies</span>
                <strong className="text-red-600">{Number(data?.active_emergencies ?? 0)}</strong>
              </div>
              <div className="flex justify-between items-center pb-2 border-b border-gray-100">
                <span className="text-sm text-ink">Critical Inventory</span>
                <strong className="text-orange-600">{Number(data?.critical_inventory ?? 0)}</strong>
              </div>
              <div className="flex justify-between items-center pb-2 border-b border-gray-100">
                <span className="text-sm text-ink">Transfer Requests</span>
                <strong className="text-blue-600">{Number(data?.total_transfers ?? 0)}</strong>
              </div>
            </div>
            <div className={`mt-auto p-3 rounded-lg text-center font-bold text-sm ${requiresAttention ? 'bg-red-100 text-red-700' : 'bg-green-100 text-green-700'}`}>
              {requiresAttention ? 'ATTENTION REQUIRED' : 'ALL SYSTEMS NORMAL'}
            </div>
          </div>
        </div>

        {/* Network Overview */}
        <div className="panel shadow-md border border-border">
          <div className="panel-title mb-5">Network Overview</div>
          <div className="space-y-4">
            <div className="flex justify-between items-center p-3 rounded-lg bg-gray-50">
              <span className="text-sm font-medium text-ink">Facilities</span>
              <strong className="text-lg text-ink">{Number(data?.facilities ?? 0)}</strong>
            </div>
            <div className="flex justify-between items-center p-3 rounded-lg bg-gray-50">
              <span className="text-sm font-medium text-ink">Medicines</span>
              <strong className="text-lg text-ink">{Number(data?.medicines ?? 0)}</strong>
            </div>
            <div className="flex justify-between items-center p-3 rounded-lg bg-gray-50">
              <span className="text-sm font-medium text-ink">Inventory</span>
              <strong className="text-lg text-ink">{totalInventory}</strong>
            </div>
            <div className="flex justify-between items-center p-3 rounded-lg bg-gray-50">
              <span className="text-sm font-medium text-ink">Coverage</span>
              <strong className="text-lg text-green-600">{healthScore}%</strong>
            </div>
          </div>
        </div>

        {/* Recent Transfers List */}
        <div className="panel shadow-md border border-border flex flex-col">
          <div className="panel-title mb-5">Recent Transfers</div>
          <div className="flex-1 flex flex-col items-center justify-center text-ink-faint space-y-2 pb-4">
            <svg className="w-8 h-8 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4" />
            </svg>
            <p className="text-sm">Awaiting Transfer API Connection</p>
            <button className="text-xs text-blue-600 hover:underline mt-2" onClick={() => navigate('/transfers')}>
              Go to Transfers Page
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}