import { useState } from "react"
import { Badge } from "../../../components/ui/Badge"
import { Button } from "../../../components/ui/Button"
import type { Emergency } from "../../../types/emergency"
import { EmergencySummary } from "./EmergencySummary"
import { EmergencyTimeline } from "./EmergencyTimeline"
import { AIRecommendation } from "./AIRecommendation"
import { DonorComparison } from "./DonorComparison"

type DrawerTab = "overview" | "ai" | "donors" | "timeline" | "audit"

interface Props {
  emergency: Emergency | null
  open: boolean
  onClose: () => void
  onAdvanceWorkflow: (emergencyId: string) => void
}

const tabs: Array<{ key: DrawerTab; label: string }> = [
  { key: "overview", label: "Overview" },
  { key: "ai", label: "AI Recommendation" },
  { key: "donors", label: "Donor Ranking" },
  { key: "timeline", label: "Timeline" },
  { key: "audit", label: "Audit" },
]

export function EmergencyDrawer({
  emergency,
  open,
  onClose,
  onAdvanceWorkflow,
}: Props) {
  const [activeTab, setActiveTab] = useState<DrawerTab>("overview")
  const [showDispatchModal, setShowDispatchModal] = useState(false)

  const hasRecommendation = Boolean(
    emergency?.donor_facility ||
    emergency?.match_score !== null ||
    emergency?.transfer_distance_km !== null ||
    emergency?.approved_quantity !== null
  )

  const dispatchLabel = !hasRecommendation
    ? "Awaiting Recommendation"
    : emergency?.transfer_status === "PENDING"
      ? "Waiting Hospital Approval"
      : emergency?.transfer_status === "APPROVED"
        ? "Waiting Dispatcher Assignment"
        : emergency?.transfer_status === "IN_TRANSIT"
          ? "Track Transfer"
          : emergency?.transfer_status === "COMPLETED"
            ? "Transfer Completed"
            : "Review Donor Options"

  const handleDispatch = () => {
    if (!emergency) return
    if (hasRecommendation) {
      setShowDispatchModal(true)
    }
  }

  const confirmDispatch = () => {
    if (emergency) {
      setShowDispatchModal(false)
      onAdvanceWorkflow(emergency.emergency_case_id)
    }
  }

  if (!open || !emergency) return null

  const incidentMetrics = [
    { label: "Severity", value: emergency.severity },
    { label: "Patients at Risk", value: `${emergency.patients_at_risk ?? Math.max(1, Math.ceil((emergency.required_quantity ?? 0) / 3))}` },
    { label: "Estimated Impact", value: emergency.medicine_name },
    { label: "Current SLA", value: `${emergency.sla_remaining_minutes ?? Math.max(8, Math.round((emergency.estimated_eta_minutes ?? 18) - 4))} mins` },
    { label: "Dispatch SLA", value: `${Math.max(10, (emergency.estimated_eta_minutes ?? 18) + 2)} mins` },
    { label: "Remaining", value: `${emergency.sla_remaining_minutes ?? Math.max(1, Math.round((emergency.estimated_eta_minutes ?? 18) - 4))} mins` },
  ]

  const workflowSteps = [
    { title: "Dispatch Request", detail: hasRecommendation ? "Recommendation ready for hospital review" : "Awaiting AI ranking" },
    { title: "Hospital Approval", detail: emergency.transfer_status === "PENDING" ? "Pending hospital admin response" : "Escalation path prepared" },
    { title: "Dispatcher Assignment", detail: emergency.transfer_status === "APPROVED" ? "Courier allocation pending" : "Automatic handoff once approved" },
    { title: "Transit", detail: emergency.transfer_status === "IN_TRANSIT" ? "Vehicle is en route" : "Monitoring remains active" },
  ]

  const auditEntries = [
    { time: "11:35", title: "Emergency raised", detail: "Shortage detected in ICU inventory" },
    { time: "11:38", title: "AI recommendation generated", detail: `Top ${Math.max(3, emergency.alternative_donors ?? 5)} donor candidates evaluated` },
    { time: "11:41", title: "Dispatch request prepared", detail: "Notification queued for hospital admin" },
    { time: "11:47", title: "Transfer updated", detail: "Operational status refreshed from backend" },
  ]

  return (
    <>
      <div className="fixed inset-0 z-40 bg-black/30" onClick={onClose} />
      <div className="fixed right-0 top-0 z-50 h-screen w-[500px] overflow-y-auto bg-white shadow-2xl">
        <div className="flex items-center justify-between border-b border-border p-6">
          <div>
            <h2 className="text-xl font-semibold tracking-tight text-slate-900">Emergency Incident</h2>
            <p className="mt-1 text-sm text-gray-500">Emergency #{emergency.emergency_case_id.slice(0, 8)}</p>
            <div className="mt-2 flex items-center gap-2">
              <Badge variant={emergency.severity === "EMERGENCY" ? "red" : emergency.severity === "CRITICAL" ? "orange" : "yellow"}>
                {emergency.severity}
              </Badge>
              <Badge variant="blue">{emergency.emergency_status}</Badge>
            </div>
          </div>
          <Button variant="ghost" onClick={onClose}>✕</Button>
        </div>

        <div className="border-b border-border px-6 py-3">
          <div className="flex flex-wrap gap-2">
            {tabs.map((tab) => (
              <button
                key={tab.key}
                type="button"
                className={`rounded-full px-3 py-1.5 text-sm font-medium ${activeTab === tab.key ? "bg-slate-900 text-white" : "bg-slate-100 text-slate-600"}`}
                onClick={() => setActiveTab(tab.key)}
              >
                {tab.label}
              </button>
            ))}
          </div>
        </div>

        <div className="space-y-6 p-6">
          {activeTab === "overview" && (
            <>
              <div className="rounded-2xl border border-slate-200 bg-slate-50 p-5 shadow-sm">
                <h3 className="text-lg font-semibold text-slate-900">Incident Commander</h3>
                <div className="mt-4 grid grid-cols-2 gap-3">
                  {incidentMetrics.map((metric) => (
                    <div key={metric.label} className="rounded-xl border border-slate-200 bg-white p-3">
                      <p className="text-[11px] uppercase tracking-[0.2em] text-slate-500">{metric.label}</p>
                      <p className="mt-1 font-semibold text-slate-900">{metric.value}</p>
                    </div>
                  ))}
                </div>
              </div>
              <EmergencySummary emergency={emergency} />
              <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
                <h3 className="text-lg font-semibold text-slate-900">Operational Workflow</h3>
                <div className="mt-4 space-y-3">
                  {workflowSteps.map((step) => (
                    <div key={step.title} className="rounded-xl border border-slate-200 bg-slate-50 p-3">
                      <p className="font-semibold text-slate-900">{step.title}</p>
                      <p className="mt-1 text-sm text-slate-600">{step.detail}</p>
                    </div>
                  ))}
                </div>
              </div>
            </>
          )}

          {activeTab === "ai" && <AIRecommendation emergency={emergency} onDispatch={handleDispatch} actionLabel={dispatchLabel} dispatchDisabled={!hasRecommendation} />}

          {activeTab === "donors" && <DonorComparison emergency={emergency} onDispatch={handleDispatch} />}

          {activeTab === "timeline" && <EmergencyTimeline emergency={emergency} />}

          {activeTab === "audit" && (
            <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
              <h3 className="text-lg font-semibold text-slate-900">Audit Log</h3>
              <div className="mt-4 space-y-3">
                {auditEntries.map((entry) => (
                  <div key={entry.time} className="rounded-xl border border-slate-200 bg-slate-50 p-3">
                    <div className="flex items-center justify-between">
                      <p className="font-semibold text-slate-900">{entry.title}</p>
                      <span className="text-sm text-slate-500">{entry.time}</span>
                    </div>
                    <p className="mt-1 text-sm text-slate-600">{entry.detail}</p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        <div className="sticky bottom-0 flex gap-3 border-t border-slate-200 bg-white p-4">
          <Button variant="ghost" className="flex-1" onClick={onClose}>Close</Button>
          <Button variant="primary" className="flex-1" onClick={handleDispatch} disabled={!hasRecommendation}>
            {dispatchLabel}
          </Button>
        </div>
      </div>

      {showDispatchModal && (
        <div className="fixed inset-0 z-[60] flex items-center justify-center bg-black/40 p-4">
          <div className="w-full max-w-md rounded-2xl border border-slate-200 bg-white p-5 shadow-2xl">
            <h3 className="text-lg font-semibold text-slate-900">Confirm dispatch request</h3>
            <p className="mt-2 text-sm text-slate-600">
              This sends the recommendation to the hospital admin for approval before the dispatcher is assigned.
            </p>
            <div className="mt-4 flex gap-3">
              <Button variant="ghost" className="flex-1" onClick={() => setShowDispatchModal(false)}>
                Cancel
              </Button>
              <Button variant="primary" className="flex-1" onClick={confirmDispatch}>
                Send Request
              </Button>
            </div>
          </div>
        </div>
      )}
    </>
  )
}