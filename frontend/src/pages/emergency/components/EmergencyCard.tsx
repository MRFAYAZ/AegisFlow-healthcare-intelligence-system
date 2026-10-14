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

const statusVariant: Record<string, "red" | "orange" | "green" | "blue"> = {
  ACTIVE: "red",
  MATCHING: "orange",
  PARTIALLY_RESOLVED: "blue",
  RESOLVED: "green",
  CLOSED: "green",
}

export function EmergencyCard({ emergency, onView }: Props) {
  const remaining = Math.max(
    0,
    Number(emergency.required_quantity ?? 0) - Number(emergency.available_quantity ?? 0),
  )
  const hasTransfer = Boolean(emergency.transfer_id)

  return (
    <article className="rounded-xl border border-border bg-white shadow-sm transition-all hover:shadow-md">
      <div className="flex items-center justify-between border-b border-border p-5">
        <div>
          <div className="text-lg font-semibold text-ink">{emergency.medicine_name}</div>
          <div className="mt-1 text-sm text-ink-muted">{emergency.facility_name}</div>
        </div>
        <Badge variant={severityVariant[emergency.severity] ?? "yellow"}>{emergency.severity}</Badge>
      </div>

      <div className="space-y-3 p-5">
        <div className="grid grid-cols-2 gap-3">
          <Metric label="Remaining demand" value={`${remaining} units`} />
          <Metric label="Target quantity" value={`${emergency.required_quantity} units`} />
          <Metric
            label="Match score"
            value={hasTransfer && emergency.match_score !== null
              ? `${Number(emergency.match_score).toFixed(1)} / 100`
              : "Not ranked yet"}
          />
          <Metric
            label="Geographic distance"
            value={hasTransfer && emergency.transfer_distance_km !== null
              ? `${Number(emergency.transfer_distance_km).toFixed(1)} km straight-line`
              : "Not available"}
          />
        </div>

        <div className="flex items-center justify-between gap-2">
          <span className="text-ink-muted">Transfer state</span>
          <Badge variant={hasTransfer ? "blue" : "orange"}>
            {emergency.transfer_status?.replaceAll("_", " ") ?? "NOT REQUESTED"}
          </Badge>
        </div>
        <div className="flex items-center justify-between gap-2">
          <span className="text-ink-muted">Emergency state</span>
          <Badge variant={statusVariant[emergency.emergency_status] ?? "orange"}>
            {emergency.emergency_status.replaceAll("_", " ")}
          </Badge>
        </div>
        <div className="flex items-center justify-between gap-2">
          <span className="text-ink-muted">Shortage score</span>
          <strong>{Number(emergency.shortage_score).toFixed(1)} / 100</strong>
        </div>
        <div className="flex items-center justify-between gap-2">
          <span className="text-ink-muted">Search radius</span>
          <strong>{emergency.emergency_radius_km} km</strong>
        </div>
      </div>

      <div className="flex gap-3 border-t border-border p-4">
        <Button variant="ghost" className="flex-1" onClick={() => onView(emergency)}>
          View Details
        </Button>
        <Button variant="primary" className="flex-1" onClick={() => onView(emergency)}>
          Review Supply Options
        </Button>
      </div>
    </article>
  )
}

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-lg bg-slate-50 p-3">
      <p className="text-[10px] uppercase tracking-wide text-slate-500">{label}</p>
      <p className="mt-1 break-words font-semibold text-slate-900">{value}</p>
    </div>
  )
}
