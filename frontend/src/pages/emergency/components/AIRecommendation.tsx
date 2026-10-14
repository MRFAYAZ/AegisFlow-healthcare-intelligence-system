import { Badge } from "../../../components/ui/Badge"
import { Button } from "../../../components/ui/Button"
import type { Emergency } from "../../../types/emergency"

interface Props {
  emergency: Emergency
  onDispatch: () => void
  actionLabel: string
  dispatchDisabled: boolean
}

export function AIRecommendation({
  emergency,
  onDispatch,
  actionLabel,
  dispatchDisabled,
}: Props) {
  const hasTransfer = Boolean(emergency.transfer_id)
  const score = emergency.match_score === null ? null : Number(emergency.match_score)
  const outstanding = Math.max(
    0,
    Number(emergency.required_quantity ?? 0) - Number(emergency.available_quantity ?? 0),
  )
  const distance = emergency.transfer_distance_km === null
    ? null
    : Number(emergency.transfer_distance_km)

  const statusTone = emergency.transfer_status === "COMPLETED"
    ? "green"
    : emergency.transfer_status === "REJECTED"
      ? "red"
      : emergency.transfer_status === "IN_TRANSIT"
        ? "blue"
        : "yellow"

  return (
    <section className="space-y-4 rounded-xl border bg-white p-5 shadow-sm">
      <div className="flex items-start justify-between gap-3">
        <div>
          <h3 className="text-lg font-semibold text-slate-900">Explainable sourcing decision</h3>
          <p className="text-sm text-slate-500">
            AegisFlow uses deterministic donor scoring for this prototype. This is not a trained machine-learning probability.
          </p>
        </div>
        {hasTransfer && emergency.transfer_status && (
          <Badge variant={statusTone}>{emergency.transfer_status.replaceAll("_", " ")}</Badge>
        )}
      </div>

      <div className="grid grid-cols-2 gap-3">
        <Info label="Requested target" value={`${emergency.required_quantity} units`} />
        <Info label="Currently available" value={`${emergency.available_quantity} units`} />
        <Info label="Remaining demand" value={`${outstanding} units`} />
        <Info label="Shortage score" value={`${Number(emergency.shortage_score).toFixed(1)} / 100`} />
        {hasTransfer && (
          <>
            <Info label="Selected donor" value={emergency.donor_facility ?? "Name unavailable"} />
            <Info label="Requested quantity" value={`${emergency.approved_quantity ?? "Pending decision"}${emergency.approved_quantity === null ? "" : " units"}`} />
            <Info label="Match score" value={score === null ? "Not recorded" : `${score.toFixed(1)} / 100`} />
            <Info label="Straight-line distance" value={distance === null ? "Not recorded" : `${distance.toFixed(2)} km`} />
          </>
        )}
      </div>

      <div className="rounded-lg border border-slate-200 bg-slate-50 p-4">
        <h4 className="font-semibold text-slate-900">Decision explanation</h4>
        <p className="mt-2 text-sm text-slate-700">
          {emergency.ai_reason
            ?? (hasTransfer
              ? "The backend recorded a transfer recommendation, but did not return a detailed explanation."
              : "No transfer request has been created yet. Open Donor Ranking to inspect current eligible sources and their score breakdowns.")}
        </p>
        {emergency.cascade_safe === true && hasTransfer && (
          <p className="mt-2 text-sm text-emerald-800">
            The transfer record marks this recommendation as cascade-safe. Stock is revalidated again during hospital approval.
          </p>
        )}
        {emergency.cascade_safe === false && (
          <p className="mt-2 text-sm text-red-800">
            This transfer is marked as potentially unsafe for donor stock protection. Do not approve it without resolving the risk.
          </p>
        )}
      </div>

      <div className="rounded-lg border border-blue-100 bg-blue-50 p-4 text-sm text-blue-900">
        <p className="font-semibold">Human authorization remains required</p>
        <p className="mt-1">
          A donor score is a recommendation, not permission to move stock. The destination hospital must approve the quantity; only then can operations assign transport and dispatch.
        </p>
        <p className="mt-2 text-xs text-blue-800">
          Geographic distance is a straight-line estimate. A road route or delivery ETA is not available from this matching result.
        </p>
      </div>

      <Button className="w-full" variant="green" onClick={onDispatch} disabled={dispatchDisabled}>
        {actionLabel}
      </Button>
    </section>
  )
}

function Info({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-lg border p-3">
      <p className="text-xs text-gray-500">{label}</p>
      <p className="mt-1 font-semibold text-slate-900">{value}</p>
    </div>
  )
}
