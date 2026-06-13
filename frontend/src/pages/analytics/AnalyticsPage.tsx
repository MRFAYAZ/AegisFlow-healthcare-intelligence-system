import { KPICard } from '../../components/ui/KPICard'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, LineChart, Line, AreaChart, Area, PieChart, Pie, Cell, Legend } from 'recharts'

const weeklyShortages = [
  { day:'Mon', count:62 },{ day:'Tue', count:58 },{ day:'Wed', count:54 },
  { day:'Thu', count:51 },{ day:'Fri', count:49 },{ day:'Sat', count:52 },{ day:'Sun', count:47 },
]
const categoryDemand = [
  { name:'Antibiotics', value:28 },{ name:'Endocrine', value:22 },
  { name:'Emergency', value:18 },{ name:'Analgesic', value:15 },{ name:'Other', value:17 },
]
const redistribution = [
  { month:'Aug', rate:88 },{ month:'Sep', rate:90 },{ month:'Oct', rate:91 },
  { month:'Nov', rate:93 },{ month:'Dec', rate:94 },{ month:'Jan', rate:94.2 },
]
const regionData = [
  { region:'Koramangala', shortages:12 },{ region:'Whitefield', shortages:9 },
  { region:'Jayanagar', shortages:8 },{ region:'Rajajinagar', shortages:6 },
  { region:'JP Nagar', shortages:5 },{ region:'Bannerghatta', shortages:7 },
]

const PIE_COLORS = ['#2563eb','#16a34a','#dc2626','#d97706','#9a9890']

export function AnalyticsPage() {
  return (
    <div>
      <div className="grid grid-cols-4 gap-3 mb-4">
        <KPICard label="Redistribution rate" value="94.2%" sub="+2.1% this week" trend="up" color="blue" />
        <KPICard label="Avg resolution time" value="2.4h" sub="−18 min vs last week" trend="up" color="green" />
        <KPICard label="Outbreak signals" value="2" sub="Dengue demand spike detected" color="orange" />
        <KPICard label="Wastage (expiry)" value="₹1.2L" sub="−30% vs last month" trend="up" color="red" />
      </div>

      <div className="grid grid-cols-2 gap-3 mb-3">
        <div className="panel">
          <div className="panel-title mb-3">Weekly shortage trend</div>
          <ResponsiveContainer width="100%" height={200}>
            <AreaChart data={weeklyShortages}>
              <defs>
                <linearGradient id="blueGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#2563eb" stopOpacity={0.1}/>
                  <stop offset="95%" stopColor="#2563eb" stopOpacity={0}/>
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#e5e3de" vertical={false}/>
              <XAxis dataKey="day" tick={{ fontSize:11, fill:'#9a9890' }} axisLine={false} tickLine={false}/>
              <YAxis tick={{ fontSize:11, fill:'#9a9890' }} axisLine={false} tickLine={false}/>
              <Tooltip contentStyle={{ fontSize:12, borderRadius:8, border:'1px solid #e5e3de' }}/>
              <Area type="monotone" dataKey="count" stroke="#2563eb" strokeWidth={2} fill="url(#blueGrad)" dot={{ r:3, fill:'#2563eb' }}/>
            </AreaChart>
          </ResponsiveContainer>
        </div>

        <div className="panel">
          <div className="panel-title mb-3">Medicine category demand</div>
          <ResponsiveContainer width="100%" height={200}>
            <PieChart>
              <Pie data={categoryDemand} cx="45%" cy="50%" innerRadius={55} outerRadius={80} dataKey="value" paddingAngle={2}>
                {categoryDemand.map((_, i) => <Cell key={i} fill={PIE_COLORS[i % PIE_COLORS.length]}/>)}
              </Pie>
              <Legend iconSize={10} iconType="circle" wrapperStyle={{ fontSize:11, color:'#6b6860' }}/>
              <Tooltip contentStyle={{ fontSize:12, borderRadius:8, border:'1px solid #e5e3de' }}/>
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-3">
        <div className="panel">
          <div className="panel-title mb-3">Redistribution rate (6 months)</div>
          <ResponsiveContainer width="100%" height={180}>
            <LineChart data={redistribution}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e5e3de" vertical={false}/>
              <XAxis dataKey="month" tick={{ fontSize:11, fill:'#9a9890' }} axisLine={false} tickLine={false}/>
              <YAxis domain={[85,96]} tick={{ fontSize:11, fill:'#9a9890' }} axisLine={false} tickLine={false}/>
              <Tooltip contentStyle={{ fontSize:12, borderRadius:8, border:'1px solid #e5e3de' }} formatter={(v) => [`${v}%`,'Rate']}/>
              <Line type="monotone" dataKey="rate" stroke="#16a34a" strokeWidth={2.5} dot={{ r:3, fill:'#16a34a' }}/>
            </LineChart>
          </ResponsiveContainer>
        </div>

        <div className="panel">
          <div className="panel-title mb-3">Shortages by region</div>
          <ResponsiveContainer width="100%" height={180}>
            <BarChart data={regionData} layout="vertical" barSize={14}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e5e3de" horizontal={false}/>
              <XAxis type="number" tick={{ fontSize:10, fill:'#9a9890' }} axisLine={false} tickLine={false}/>
              <YAxis dataKey="region" type="category" tick={{ fontSize:10, fill:'#6b6860' }} axisLine={false} tickLine={false} width={80}/>
              <Tooltip contentStyle={{ fontSize:12, borderRadius:8, border:'1px solid #e5e3de' }}/>
              <Bar dataKey="shortages" fill="#2563eb" radius={[0,4,4,0]}/>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  )
}
