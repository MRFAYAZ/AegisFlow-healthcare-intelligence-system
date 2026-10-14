import type { Emergency } from "../../../types/emergency"

interface Props {
  emergency: Emergency
}

export function EmergencySummary({ emergency }: Props) {
  const phase = emergency.emergency_status === "RESOLVED" || emergency.emergency_status === "CLOSED"
    ? "Resolved"
    : emergency.transfer_status === "COMPLETED"
      ? emergency.emergency_status === "PARTIALLY_RESOLVED" ? "Partially fulfilled" : "Transfer completed"
      : emergency.transfer_status === "IN_TRANSIT"
        ? "In transit"
        : emergency.transfer_status === "APPROVED"
          ? "Approved — awaiting dispatch"
          : emergency.transfer_status === "PENDING"
            ? "Awaiting hospital decision"
            : emergency.transfer_status === "REJECTED"
              ? "Transfer rejected — alternatives may be requested"
              : emergency.emergency_status === "MATCHING"
                ? "Matching / sourcing"
                : "Awaiting donor request"

  const remaining = Math.max(
    0,
    Number(emergency.required_quantity ?? 0) - Number(emergency.available_quantity ?? 0),
  )

  const fields = [
    { label: "Medicine", value: emergency.medicine_name },
    { label: "Receiving facility", value: emergency.facility_name },
    { label: "Requested target", value: `${emergency.required_quantity} units` },
    { label: "Available at facility", value: `${emergency.available_quantity} units` },
    { label: "Remaining quantity", value: `${remaining} units` },
    { label: "Severity", value: emergency.severity },
    { label: "Shortage score", value: `${Number(emergency.shortage_score).toFixed(1)} / 100` },
    { label: "Emergency radius", value: `${emergency.emergency_radius_km} km` },
    { label: "Current phase", value: phase },
    ...(emergency.donor_facility ? [{ label: "Current transfer donor", value: emergency.donor_facility }] : []),
    ...(emergency.requested_at ? [{ label: "Transfer requested", value: new Date(emergency.requested_at).toLocaleString() }] : []),
    ...(emergency.approved_at ? [{ label: "Decision recorded", value: new Date(emergency.approved_at).toLocaleString() }] : []),
    ...(emergency.dispatched_at ? [{ label: "Dispatched", value: new Date(emergency.dispatched_at).toLocaleString() }] : []),
    ...(emergency.delivered_at ? [{ label: "Delivered", value: new Date(emergency.delivered_at).toLocaleString() }] : []),
  ]

  return (
    <section className="space-y-4 rounded-xl border bg-slate-50 p-5">
      <h3 className="text-lg font-semibold text-slate-900">Incident overview</h3>
      <div className="grid grid-cols-2 gap-3">
        {fields.map((field) => (
          <Info key={field.label} label={field.label} value={field.value} />
        ))}
      </div>
      {emergency.rejection_reason && (
        <div className="rounded-lg border border-amber-200 bg-amber-50 p-3 text-sm text-amber-900">
          <span className="font-medium">Last rejection reason:</span> {emergency.rejection_reason}
        </div>
      )}
    </section>
  )
}

function Info({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-lg border border-slate-200 bg-white p-3">
      <p className="text-xs text-slate-500">{label}</p>
      <p className="mt-1 break-words font-semibold text-slate-900">{value}</p>
    </div>
  )
}
