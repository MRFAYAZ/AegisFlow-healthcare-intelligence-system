import { useNavigate } from 'react-router-dom'
import { useAppStore } from '../../store/useAppStore'
import { KPICard } from '../../components/ui/KPICard'
import { EmergencyBanner } from '../../components/ui/EmergencyBanner'
import { mockAlerts } from '../../lib/mockData'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, LineChart, Line } from 'recharts'

const severityData = [
  { name:'Emergency', value:3, fill:'#dc2626' },
  { name:'Critical', value:12, fill:'#ea580c' },
  { name:'Warning', value:18, fill:'#d97706' },
  { name:'Low', value:14, fill:'#16a34a' },
]

const trendData = [
  { day:'Mon', count:62 },{ day:'Tue', count:58 },{ day:'Wed', count:54 },
  { day:'Thu', count:51 },{ day:'Fri', count:49 },{ day:'Sat', count:52 },{ day:'Sun', count:47 },
]

const facilityStatus = [
  { label:'Fully stocked', count:614, color:'#16a34a' },
  { label:'Low stock',     count:178, color:'#d97706' },
  { label:'Critical',      count:43,  color:'#ea580c' },
  { label:'Emergency',     count:12,  color:'#dc2626' },
]

const timeline = [
  { label:'Emergency transfer approved — Insulin', meta:'City General → Apollo · 4 min ago', color:'#2563eb' },
  { label:'Shortage signal — Dialysis Fluid', meta:'Jayanagar Regional · 22 min ago', color:'#ea580c' },
  { label:'Stock replenished — Paracetamol IV', meta:"St. John's · 1h ago", color:'#16a34a' },
  { label:'New facility onboarded', meta:'Narayana Health, Rajajinagar · 3h ago', color:'#9a9890' },
]

const alertColors: Record<string, string> = { emergency:'#dc2626', critical:'#ea580c', warning:'#d97706', resolved:'#16a34a' }
const alertLabels: Record<string, string> = { emergency:'Emergency', critical:'Critical', warning:'Warning', resolved:'Resolved' }

export function DashboardPage() {
  const navigate = useNavigate()
  const { emergencies, transfers } = useAppStore()
  const activeEmer = emergencies.filter(e => e.status !== 'resolved').length
  const pendingTf = transfers.filter(t => t.status === 'pending' || t.status === 'in_transit').length

  return (
    <div>
      <EmergencyBanner count={activeEmer} onView={() => navigate('/emergency')} />

      {/* KPIs */}
      <div className="grid grid-cols-4 gap-3 mb-4">
        <KPICard label="Total facilities" value="847" sub="+12 this month" trend="up" color="blue" />
        <KPICard label="Medicines tracked" value="24,310" sub="98.2% availability" trend="up" color="green" />
        <KPICard label="Active shortages" value={activeEmer + 44} sub="+5 since yesterday" trend="down" color="red" />
        <KPICard label="Transfers pending" value={pendingTf} sub="Avg 2.4hr resolution" color="orange" />
      </div>

      {/* Row 1 */}
      <div className="grid grid-cols-3 gap-3 mb-3">
        <div className="col-span-2 panel">
          <div className="panel-title mb-3">Shortage severity</div>
          <ResponsiveContainer width="100%" height={170}>
            <BarChart data={severityData} barSize={36}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e5e3de" vertical={false} />
              <XAxis dataKey="name" tick={{ fontSize:11, fill:'#9a9890' }} axisLine={false} tickLine={false} />
              <YAxis tick={{ fontSize:11, fill:'#9a9890' }} axisLine={false} tickLine={false} />
              <Tooltip contentStyle={{ fontSize:12, borderRadius:8, border:'1px solid #e5e3de', boxShadow:'0 2px 8px rgba(0,0,0,0.06)' }} />
              <Bar dataKey="value" radius={[4,4,0,0]}>
                {severityData.map((entry, i) => (
                  <rect key={i} fill={entry.fill} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="panel">
          <div className="panel-title mb-3">Facility status</div>
          {facilityStatus.map(f => (
            <div key={f.label} className="stat-row">
              <div className="flex items-center gap-2 text-[12px] text-ink">
                <span className="w-2 h-2 rounded-full" style={{ background: f.color }} />
                {f.label}
              </div>
              <div className="text-[12px] font-semibold" style={{ color: f.color }}>{f.count}</div>
            </div>
          ))}
        </div>
      </div>

      {/* Row 2 */}
      <div className="grid grid-cols-3 gap-3 mb-3">
        <div className="panel">
          <div className="panel-title mb-3">Weekly trend</div>
          <ResponsiveContainer width="100%" height={130}>
            <LineChart data={trendData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e5e3de" vertical={false} />
              <XAxis dataKey="day" tick={{ fontSize:10, fill:'#9a9890' }} axisLine={false} tickLine={false} />
              <YAxis tick={{ fontSize:10, fill:'#9a9890' }} axisLine={false} tickLine={false} />
              <Tooltip contentStyle={{ fontSize:12, borderRadius:8, border:'1px solid #e5e3de' }} />
              <Line type="monotone" dataKey="count" stroke="#2563eb" strokeWidth={2} dot={{ r:3, fill:'#2563eb' }} />
            </LineChart>
          </ResponsiveContainer>
        </div>

        <div className="panel">
          <div className="panel-title mb-3">Recent alerts</div>
          {mockAlerts.map(a => (
            <div key={a.id} className="alert-row">
              <div className="alert-dot" style={{ background: alertColors[a.type] }} />
              <div className="flex-1 text-[12px] text-ink leading-snug">
                <strong>{alertLabels[a.type]}</strong> — {a.message}
              </div>
              <div className="text-[10px] text-ink-faint whitespace-nowrap">{a.time}</div>
            </div>
          ))}
        </div>

        <div className="panel">
          <div className="panel-title mb-3">Activity timeline</div>
          {timeline.map((t, i) => (
            <div key={i} className="flex gap-3 py-2">
              <div className="flex flex-col items-center flex-shrink-0">
                <div className="w-2 h-2 rounded-full border-2 flex-shrink-0" style={{ background: t.color, borderColor: t.color + '40' }} />
                {i < timeline.length - 1 && <div className="w-px flex-1 bg-border mt-1 min-h-[14px]" />}
              </div>
              <div className="pb-1">
                <div className="text-[12px] text-ink">{t.label}</div>
                <div className="text-[10px] text-ink-faint mt-0.5">{t.meta}</div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
