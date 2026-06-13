const accentColors = { blue:'#2563eb', green:'#16a34a', red:'#dc2626', orange:'#ea580c' }
interface KPICardProps {
  label: string
  value: string | number
  sub: string
  trend?: 'up'|'down'|'neutral'
  color: 'blue'|'green'|'red'|'orange'
  icon?: string
}
export function KPICard({ label, value, sub, trend, color }: KPICardProps) {
  const trendColor = trend==='up' ? '#16a34a' : trend==='down' ? '#dc2626' : '#9a9890'
  const trendIcon = trend==='up' ? '↑' : trend==='down' ? '↓' : ''
  return (
    <div className="kpi-card">
      <div className="flex justify-between items-start">
        <div className="kpi-label">{label}</div>
        <div style={{ width:3, height:28, borderRadius:3, background: accentColors[color] }} />
      </div>
      <div className="kpi-value">{value}</div>
      <div className="kpi-sub" style={{ color: trendColor }}>
        {trendIcon && <span>{trendIcon}</span>}
        <span>{sub}</span>
      </div>
    </div>
  )
}
