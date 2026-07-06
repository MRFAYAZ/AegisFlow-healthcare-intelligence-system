import { Badge } from "../../../components/ui/Badge"
import { Button } from "../../../components/ui/Button"
import type { Emergency } from "../../../types/emergency"

interface Props {
  emergency: Emergency
  onDispatch: () => void
  onViewAlternatives: () => void
}

export function EmergencyDecisionCard({ emergency, onDispatch, onViewAlternatives }: Props) {
  const confidence = Number(emergency.match_score ?? 0)
  const eta = emergency.estimated_eta_minutes ?? Math.max(10, Math.round((emergency.transfer_distance_km ?? 0) * 2.2))
  const riskLevel = emergency.cascade_safe === false ? "MEDIUM" : "LOW"

  return (
    <div className="rounded-2xl border border-slate-200 bg-gradient-to-br from-slate-50 to-white p-5 shadow-sm">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">
            Recommended Action
          </p>
          <h3 className="mt-1 text-lg font-semibold text-slate-900">
            Dispatch from {emergency.donor_facility ?? "recommended donor"}
          </h3>
        </div>
        <Badge variant="green">{confidence.toFixed(1)}% confidence</Badge>
      </div>

      <div className="space-y-3 rounded-xl border border-slate-200 bg-white p-4">
        <div className="flex items-center justify-between text-sm">
          <span className="text-slate-500">Confidence</span>
          <span className="font-semibold text-slate-900">{confidence.toFixed(1)}%</span>
        </div>
        <div className="flex items-center justify-between text-sm">
          <span className="text-slate-500">ETA</span>
          <span className="font-semibold text-slate-900">{eta} mins</span>
        </div>
        <div className="flex items-center justify-between text-sm">
          <span className="text-slate-500">Risk</span>
          <span className="font-semibold text-slate-900">{riskLevel}</span>
        </div>
        <div className="flex items-center justify-between text-sm">
          <span className="text-slate-500">Alternative Donors</span>
          <span className="font-semibold text-slate-900">{emergency.alternative_donors ?? 4}</span>
        </div>
      </div>

      <div className="mt-4 rounded-xl border border-blue-200 bg-blue-50 p-4 text-sm text-blue-900">
        <p className="font-semibold">AI reasoning</p>
        <p className="mt-1">{emergency.ai_reason ?? "Highest inventory with minimum delivery distance."}</p>
      </div>

      <div className="mt-4 flex gap-3">
        <Button variant="green" className="flex-1" onClick={onDispatch}>
          Dispatch
        </Button>
        <Button variant="ghost" className="flex-1" onClick={onViewAlternatives}>
          View Alternatives
        </Button>
      </div>
    </div>
  )
}
