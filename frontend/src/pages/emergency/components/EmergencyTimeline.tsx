import type { Emergency } from "../../../types/emergency"

interface Props {
    emergency: Emergency
}

export function EmergencyTimeline({ emergency }: Props) {
    const hasRecommendation = Boolean(
        emergency.donor_facility ||
        emergency.match_score !== null ||
        emergency.transfer_distance_km !== null ||
        emergency.approved_quantity !== null
    )

    const events = [
        { time: "11:35", title: "Emergency Created", detail: "Critical shortage detected for ICU inventory" },
        { time: "11:38", title: "AI Recommendation Generated", detail: hasRecommendation ? "Donor ranking finalized" : "Awaiting donor ranking" },
        { time: "11:41", title: "Dispatch Request Sent", detail: `${emergency.donor_facility ?? "Recommended donor"} selected for hospital review` },
        { time: "11:48", title: "Hospital Approval Pending", detail: emergency.transfer_status === "PENDING" ? "Awaiting response from hospital admin" : "Approval state updated" },
        { time: "11:52", title: "Courier Allocation Pending", detail: emergency.transfer_status === "APPROVED" ? "Dispatcher assignment queued" : "Waiting for approval" },
        { time: "12:05", title: "In Transit", detail: emergency.transfer_status === "IN_TRANSIT" ? "Vehicle is en route" : "Transit will start once approval is granted" },
        { time: "12:20", title: "Delivered", detail: emergency.transfer_status === "COMPLETED" ? "Inventory received and closed" : "Delivery completion pending" },
    ]

    const currentIndex = !hasRecommendation
        ? 1
        : emergency.transfer_status === "PENDING"
            ? 3
            : emergency.transfer_status === "APPROVED"
                ? 4
                : emergency.transfer_status === "IN_TRANSIT"
                    ? 5
                    : emergency.transfer_status === "COMPLETED"
                        ? 6
                        : 2

    return (
        <div className="rounded-xl border bg-white p-5">
            <div className="mb-5 flex items-center justify-between">
                <h3 className="text-lg font-semibold text-slate-900">Operational Timeline</h3>
                <p className="text-sm text-gray-500">Last updated {new Date(emergency.triggered_at).toLocaleString()}</p>
            </div>

            <div className="space-y-4">
                {events.map((event, index) => {
                    const isComplete = index <= currentIndex
                    return (
                        <div key={event.title} className="flex items-start gap-3">
                            <div className={`flex h-7 w-7 items-center justify-center rounded-full text-xs font-semibold text-white ${isComplete ? "bg-green-600" : "bg-gray-300"}`}>
                                {isComplete ? "✓" : index + 1}
                            </div>
                            <div>
                                <div className="flex items-center gap-2">
                                    <p className="font-medium text-slate-900">{event.title}</p>
                                    <span className="text-sm text-slate-500">{event.time}</span>
                                </div>
                                <p className="text-sm text-slate-500">{event.detail}</p>
                            </div>
                        </div>
                    )
                })}
            </div>
        </div>
    )
}