import { useQuery } from "@tanstack/react-query"
import type { Emergency } from "../../../types/emergency"
import { auditAPI } from "../../../services/api"

interface Props {
    emergency: Emergency
}

interface AuditEvent {
    audit_id: string
    action_type: string
    new_value?: Record<string, unknown>
    created_at: string
}

const eventLabels: Record<string, string> = {
    EMERGENCY_CREATED: "Emergency detected",
    DONOR_MATCHING_COMPLETED: "Donor matching completed",
    ALLOCATION_APPROVED: "Allocation approved",
    INVENTORY_RESERVED: "Inventory reserved",
    DISPATCH_ASSIGNED: "Dispatch assigned",
    TRANSFER_DISPATCHED: "Shipment in transit",
    TRANSFER_DELIVERED: "Delivery confirmed",
    INVENTORY_SETTLED: "Inventory settled",
    EMERGENCY_PARTIALLY_RESOLVED: "Emergency partially resolved",
    EMERGENCY_RESOLVED: "Emergency resolved",
}

function eventDetail(event: AuditEvent) {
    const value = event.new_value ?? {}
    if (event.action_type === "DONOR_MATCHING_COMPLETED") {
        return `${value.candidate_count ?? 0} donor facilities evaluated`
    }
    if (["INVENTORY_RESERVED", "TRANSFER_DELIVERED", "INVENTORY_SETTLED"].includes(event.action_type)) {
        return `${value.quantity ?? value.approved_quantity ?? 0} units recorded`
    }
    if (event.action_type === "EMERGENCY_RESOLVED" || event.action_type === "EMERGENCY_PARTIALLY_RESOLVED") {
        return `${value.delivered_quantity ?? 0} of ${value.required_quantity ?? 0} units delivered`
    }
    return "Recorded by the AegisFlow operations workflow"
}

export function EmergencyTimeline({ emergency }: Props) {
    const { data: events = [], isLoading } = useQuery<AuditEvent[]>({
        queryKey: ["emergency-timeline", emergency.emergency_case_id],
        queryFn: async () => (await auditAPI.getEmergencyTimeline(emergency.emergency_case_id)).data,
        staleTime: 10000,
    })

    return (
        <div className="rounded-xl border bg-white p-5">
            <div className="mb-5 flex items-center justify-between">
                <h3 className="text-lg font-semibold text-slate-900">Operational Timeline</h3>
                <p className="text-sm text-gray-500">Backend audit history</p>
            </div>

            {isLoading && <p className="text-sm text-slate-500">Loading audit events...</p>}
            {!isLoading && events.length === 0 && (
                <p className="rounded-lg bg-slate-50 p-4 text-sm text-slate-500">
                    No persisted audit events are available for this emergency yet.
                </p>
            )}
            <div className="space-y-4">
                {events.map((event) => (
                    <div key={event.audit_id} className="flex items-start gap-3">
                        <div className="flex h-7 w-7 items-center justify-center rounded-full bg-green-600 text-xs font-semibold text-white">✓</div>
                        <div>
                            <div className="flex items-center gap-2">
                                <p className="font-medium text-slate-900">{eventLabels[event.action_type] ?? event.action_type}</p>
                                <span className="text-sm text-slate-500">{new Date(event.created_at).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}</span>
                            </div>
                            <p className="text-sm text-slate-500">{eventDetail(event)}</p>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    )
}