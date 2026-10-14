import type { Emergency } from "../../../types/emergency"

interface Props {
    emergency: Emergency
}

export function EmergencySummary({ emergency }: Props) {
    const currentPhase = emergency.transfer_status === "COMPLETED"
        ? "Completed"
        : emergency.transfer_status === "IN_TRANSIT"
            ? "In Transit"
            : emergency.transfer_status === "APPROVED"
                ? "Waiting Dispatcher Assignment"
                : emergency.transfer_status === "PENDING"
                    ? "Waiting Hospital Approval"
                    : "AI Recommendation Ready"

    return (
        <div className="space-y-4 rounded-xl border border-border bg-surface-muted p-5">
            <h3 className="text-lg font-semibold text-ink">Incident Overview</h3>

            <div className="grid grid-cols-2 gap-3">
                <Info label="Medicine" value={emergency.medicine_name} />
                <Info label="Facility" value={emergency.facility_name} />
                <Info label="Available Stock" value={`${emergency.available_quantity} units`} />
                <Info label="Required" value={`${emergency.required_quantity} units`} />
                <Info label="Severity" value={emergency.severity} />
                <Info label="Shortage Score" value={`${emergency.shortage_score}%`} />
                <Info label="Current Owner" value={emergency.incident_owner ?? "Hospital Admin"} />
                <Info label="Assigned Dispatcher" value={emergency.assigned_dispatcher ?? "None"} />
                <Info label="Current Phase" value={currentPhase} />
                <Info label="Incident Age" value={`${emergency.incident_age_minutes ?? 12} min`} />
                <Info label="SLA Remaining" value={`${emergency.sla_remaining_minutes ?? 8} min`} />
                <Info label="Recommended Donor" value={emergency.donor_facility ?? "Awaiting rank"} />
            </div>

            <div className="rounded-lg border border-border bg-surface-base p-3 text-sm text-ink-muted">
                <span className="font-medium text-ink">Operational impact:</span>{" "}
                High urgency response required within the current service window.
            </div>
        </div>
    )
}

function Info({ label, value }: { label: string; value: string }) {
    return (
        <div className="rounded-lg border p-3">
            <p className="text-xs text-ink-faint">{label}</p>
            <p className="font-semibold">{value}</p>
        </div>
    )
}