import { Badge } from "../../../components/ui/Badge"
import { Button } from "../../../components/ui/Button"
import type { Emergency } from "../../../types/emergency"

interface Props {
  emergency: Emergency
  onView: (emergency: Emergency) => void
}

const severityVariant: Record<string, "red" | "orange" | "yellow"> = {
  EMERGENCY: "red",
  CRITICAL: "orange",
  WARNING: "yellow",
}

const statusVariant: Record<string, "red" | "orange" | "green"> = {
  ACTIVE: "red",
  MATCHING: "orange",
  RESOLVED: "green",
}

export function EmergencyCard({ emergency, onView }: Props) {
  const matchScore = Number(emergency.match_score ?? 0)
  const eta = emergency.estimated_eta_minutes ?? Math.max(10, Math.round((emergency.transfer_distance_km ?? 0) * 2.2))
  const patients = Math.max(1, Math.ceil((emergency.required_quantity ?? 0) / 3))
  const transferStatus = emergency.transfer_status ?? "PENDING"

  return (
    <div className="emergency-incident-card">
      <div className="incident-card-header">
        <div>
          <div className="section-kicker">Incident {emergency.emergency_case_id.slice(0, 8)}</div>
          <div className="text-lg font-semibold text-ink">{emergency.medicine_name}</div>
          <div className="mt-1 text-sm text-ink-muted">{emergency.facility_name}</div>
        </div>
        <Badge variant={severityVariant[emergency.severity]}>{emergency.severity}</Badge>
      </div>

      <div className="incident-card-body space-y-3">
        <div className="grid grid-cols-2 gap-3">
          <div className="incident-metric">
            <p>Match score</p>
            <p className="mt-1 font-semibold text-ink">{matchScore.toFixed(0)}%</p>
          </div>
          <div className="incident-metric">
            <p>ETA</p>
            <p className="mt-1 font-semibold text-ink">{eta} min</p>
          </div>
          <div className="incident-metric">
            <p>Transfer</p>
            <p className="mt-1 font-semibold text-ink">{transferStatus}</p>
          </div>
          <div className="incident-metric">
            <p>Patients at risk</p>
            <p className="mt-1 font-semibold text-ink">{patients}</p>
          </div>
        </div>

        <div className="flex justify-between">
          <span className="text-ink-muted">Shortage Score</span>
          <strong>{emergency.shortage_score}</strong>
        </div>
        <div className="flex justify-between">
          <span className="text-ink-muted">Required</span>
          <strong>{emergency.required_quantity}</strong>
        </div>
        <div className="flex justify-between">
          <span className="text-ink-muted">Available</span>
          <strong className="text-red-600">{emergency.available_quantity}</strong>
        </div>
        <div className="flex justify-between">
          <span className="text-ink-muted">Radius</span>
          <strong>{emergency.emergency_radius_km} km</strong>
        </div>
        <div className="flex justify-between">
          <span className="text-ink-muted">Status</span>
          <Badge variant={statusVariant[emergency.emergency_status]}>{emergency.emergency_status}</Badge>
        </div>
      </div>

      <div className="incident-card-actions">
        <Button variant="ghost" className="flex-1" onClick={() => onView(emergency)}>
          View Details
        </Button>
        <Button variant="red" className="flex-1" onClick={() => onView(emergency)}>
          Dispatch
        </Button>
      </div>
    </div>
  )
}