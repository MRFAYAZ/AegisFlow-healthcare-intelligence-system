import { useMemo, useState } from 'react'
import { ArrowRight, BrainCircuit, Clock3, PackageSearch, ShieldAlert, TrendingDown } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import { useShortagePredictions } from '../../hooks/useShortages'
import { useAppStore } from '../../store/useAppStore'
import type { ShortageRiskAssessment } from '../../types'

const riskStyles: Record<ShortageRiskAssessment['risk_level'], { label: string; tone: string }> = {
  CRITICAL: { label: 'Critical', tone: 'risk-critical' }, HIGH: { label: 'High', tone: 'risk-high' },
  WARNING: { label: 'Warning', tone: 'risk-warning' }, SAFE: { label: 'Safe', tone: 'risk-safe' },
}

const actionLabels: Record<ShortageRiskAssessment['recommended_action'], string> = {
  SOURCE_NETWORK: 'Source network', INITIATE_PROCUREMENT: 'Initiate procurement',
  PREPARE_REPLENISHMENT: 'Prepare replenishment', CONTINUE_MONITORING: 'Continue monitoring',
}

export function ShortagePage() {
  const navigate = useNavigate()
  const user = useAppStore((state) => state.user)
  const { data: predictions = [], isLoading, isError } = useShortagePredictions()
  const [selectedId, setSelectedId] = useState<string | null>(null)
  const visiblePredictions = useMemo(() => {
    if (user?.role !== 'hospital_admin' || !user.facility) return predictions
    return predictions.filter((item) => item.facility_name.toLowerCase().includes(user.facility!.toLowerCase()))
  }, [predictions, user])
  const selected = visiblePredictions.find((item) => item.inventory_id === selectedId) ?? visiblePredictions[0]
  const counts = {
    critical: visiblePredictions.filter((item) => item.risk_level === 'CRITICAL').length,
    high: visiblePredictions.filter((item) => item.risk_level === 'HIGH').length,
    warning: visiblePredictions.filter((item) => item.risk_level === 'WARNING').length,
    atRisk: visiblePredictions.filter((item) => item.risk_level !== 'SAFE').length,
  }

  function handleAction(item: ShortageRiskAssessment) {
    if (item.risk_level === 'CRITICAL') navigate('/emergency')
    else if (item.risk_level === 'HIGH') navigate('/procurement')
    else setSelectedId(item.inventory_id)
  }

  return <div className="shortage-intelligence page-enter space-y-6 pb-12">
    <section className="shortage-hero"><div><div className="eyebrow"><BrainCircuit size={14} /> Predictive risk / forecasting engine</div><h1>Shortage Intelligence</h1><p>Early warning for stockout risk across inventory, demand, reservations, and replenishment lead time.</p></div><div className="shortage-hero-note"><TrendingDown size={18} /><span>Explainable forecast<br /><strong>No ML claims</strong></span></div></section>
    {isError && <div className="panel text-status-red">Unable to load shortage predictions from the inventory service.</div>}
    {isLoading && <div className="panel text-ink-muted">Calculating network supply risk...</div>}
    <section className="risk-kpi-grid"><RiskKpi label="Critical" value={counts.critical} detail="Source network now" tone="critical" /><RiskKpi label="High" value={counts.high} detail="Procurement window" tone="high" /><RiskKpi label="Warning" value={counts.warning} detail="Prepare replenishment" tone="warning" /><RiskKpi label="At risk" value={counts.atRisk} detail="All non-safe records" tone="neutral" /></section>
    <div className="grid gap-6 xl:grid-cols-[minmax(0,1.45fr)_minmax(320px,0.8fr)]">
      <section className="panel overflow-hidden p-0"><div className="flex items-center justify-between border-b border-border px-5 py-4"><div><h2 className="panel-title">Predicted stockouts</h2><p className="mt-1 text-xs text-ink-muted">Usable stock excludes reserved inventory.</p></div><PackageSearch size={18} className="text-brand-600" aria-hidden="true" /></div><div className="overflow-x-auto"><table className="af-table"><thead><tr><th>Medicine</th><th>Facility</th><th>Stockout</th><th>Risk</th><th>Action</th></tr></thead><tbody>{visiblePredictions.map((item) => { const style = riskStyles[item.risk_level]; return <tr key={item.inventory_id} className={selected?.inventory_id === item.inventory_id ? 'selected-risk-row' : ''} onClick={() => setSelectedId(item.inventory_id)}><td><div className="font-semibold text-ink">{item.medicine_name}</div><div className="text-[11px] text-ink-faint">{item.usable_stock} usable units</div></td><td className="text-ink-muted">{item.facility_name}</td><td><div className="font-semibold text-ink">{item.projected_stockout_days === null ? 'No forecast' : `${item.projected_stockout_days} days`}</div><div className="text-[11px] text-ink-faint">{item.daily_consumption}/day</div></td><td><span className={`risk-pill ${style.tone}`}>{style.label}</span></td><td><button className="table-action" onClick={(event) => { event.stopPropagation(); handleAction(item) }}>{actionLabels[item.recommended_action]} <ArrowRight size={13} /></button></td></tr> })}{!isLoading && visiblePredictions.length === 0 && <tr><td colSpan={5} className="py-10 text-center text-ink-muted">No inventory risk assessments are available.</td></tr>}</tbody></table></div></section>
      {selected && <ProjectionCard prediction={selected} onAction={() => handleAction(selected)} />}
    </div>
  </div>
}

function RiskKpi({ label, value, detail, tone }: { label: string; value: number; detail: string; tone: string }) { return <div className={`risk-kpi ${tone}`}><div className="flex items-center justify-between"><span>{label}</span><ShieldAlert size={16} /></div><strong>{value}</strong><small>{detail}</small></div> }

function ProjectionCard({ prediction, onAction }: { prediction: ShortageRiskAssessment; onAction: () => void }) {
  const days = prediction.projected_stockout_days ?? 0
  const horizon = Math.max(prediction.lead_time_days + prediction.safety_stock_days, 1)
  const depletion = Math.min(100, Math.max(8, (days / horizon) * 100))
  const style = riskStyles[prediction.risk_level]
  const safetyPosition = Math.min(88, Math.max(12, (prediction.safety_stock_units / Math.max(prediction.current_stock, 1)) * 100))
  return <section className="panel projection-panel"><div className="flex items-start justify-between gap-4"><div><div className="eyebrow"><Clock3 size={14} /> Stockout projection</div><h2>{prediction.medicine_name} <span>— {prediction.facility_name}</span></h2></div><span className={`risk-pill ${style.tone}`}>{style.label}</span></div><div className="projection-chart" aria-label="Projected stock depletion chart"><div className="chart-axis"><span>{prediction.current_stock}</span><span>{Math.round(prediction.safety_stock_units)} safety</span><span>0</span></div><div className="chart-area"><div className="safety-line" style={{ bottom: `${safetyPosition}%` }} /><div className="depletion-line" style={{ width: `${depletion}%` }} /><div className="current-dot" /><div className="stockout-dot" style={{ left: `${depletion}%` }} /></div><div className="chart-caption"><strong>{prediction.projected_stockout_days === null ? 'No projected stockout' : `${days} days`}</strong><span>Projected depletion</span></div></div><div className="projection-stats"><Stat label="Physical stock" value={`${prediction.current_stock}`} /><Stat label="Reserved" value={`${prediction.reserved_stock}`} /><Stat label="Usable stock" value={`${prediction.usable_stock}`} /><Stat label="Daily usage" value={`${prediction.daily_consumption}`} /></div><div className="forecast-note">Forecast uses usable stock, average daily consumption, safety stock of {prediction.safety_stock_days} days, and a {prediction.lead_time_days}-day replenishment lead time.</div><button className="btn btn-primary w-full justify-center" onClick={onAction}>{actionLabels[prediction.recommended_action]} <ArrowRight size={15} /></button></section>
}

function Stat({ label, value }: { label: string; value: string }) { return <div><span>{label}</span><strong>{value}</strong></div> }