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
  onAdvanceWorkflow: (emergencyId: string) => void | Promise<void>
}

const tabs: Array<{ key: DrawerTab; label: string }> = [
  { key: "overview", label: "Overview" },
  { key: "ai", label: "Decision Support" },
  { key: "donors", label: "Donor Ranking" },
  { key: "timeline", label: "Timeline" },
  { key: "audit", label: "Recorded Milestones" },
]

export function EmergencyDrawer({
  emergency,
  open,
  onClose,
  onAdvanceWorkflow,
}: Props) {
  const [activeTab, setActiveTab] = useState<DrawerTab>("overview")
  const [showRequestModal, setShowRequestModal] = useState(false)
  const [isSubmitting, setIsSubmitting] = useState(false)

  if (!open || !emergency) return null

  const transferStatus = emergency.transfer_status
  const requestAlreadyActive = ["PENDING", "APPROVED", "IN_TRANSIT"].includes(transferStatus ?? "")
  const emergencyClosed = ["RESOLVED", "CLOSED"].includes(emergency.emergency_status)
  const requestDisabled = requestAlreadyActive || emergencyClosed

  const requestLabel = transferStatus === "PENDING"
    ? "Transfer Awaiting Hospital Decision"
    : transferStatus === "APPROVED"
      ? "Transfer Approved — Awaiting Dispatch"
      : transferStatus === "IN_TRANSIT"
        ? "Shipment In Transit"
        : emergencyClosed
          ? "Emergency Resolved"
          : transferStatus === "COMPLETED" || emergency.emergency_status === "PARTIALLY_RESOLVED"
            ? "Request Remaining Supply"
            : transferStatus === "REJECTED"
              ? "Request from Alternative Sources"
              : "Create Transfer Requests"

  const handleRequest = () => {
    if (!requestDisabled) setShowRequestModal(true)
  }

  const confirmRequest = async () => {
    if (!emergency || requestDisabled || isSubmitting) return
    setIsSubmitting(true)
    try {
      await onAdvanceWorkflow(emergency.emergency_case_id)
      setShowRequestModal(false)
    } finally {
      setIsSubmitting(false)
    }
  }

  const incidentMetrics = [
    { label: "Severity", value: emergency.severity },
    { label: "Medicine", value: emergency.medicine_name },
    { label: "Requested target", value: `${emergency.required_quantity} units` },
    { label: "Current available", value: `${emergency.available_quantity} units` },
    { label: "Remaining quantity", value: `${Math.max(0, emergency.required_quantity - emergency.available_quantity)} units` },
    { label: "Shortage score", value: `${Number(emergency.shortage_score).toFixed(1)} / 100` },
  ]

  const workflowSteps = [
    {
      title: "Emergency registered",
      detail: new Date(emergency.triggered_at).toLocaleString(),
    },
    {
      title: "Donor discovery",
      detail: "Current eligible candidates and ranking are available in the Donor Ranking tab.",
    },
    {
      title: "Transfer request",
      detail: emergency.requested_at
        ? `Recorded ${new Date(emergency.requested_at).toLocaleString()}`
        : "No transfer request recorded yet.",
    },
    {
      title: "Hospital decision",
      detail: emergency.approved_at
        ? `Decision recorded ${new Date(emergency.approved_at).toLocaleString()}${emergency.rejection_reason ? ` — ${emergency.rejection_reason}` : ""}`
        : transferStatus === "PENDING"
          ? "Awaiting hospital approval or rejection."
          : "No hospital decision timestamp recorded.",
    },
    {
      title: "Transport",
      detail: emergency.transport_type
        ? `${emergency.transport_type}${emergency.vehicle_reference ? ` — ${emergency.vehicle_reference}` : ""}${emergency.dispatched_at ? `; dispatched ${new Date(emergency.dispatched_at).toLocaleString()}` : "; not yet dispatched"}`
        : "Transport has not been assigned.",
    },
    {
      title: "Delivery",
      detail: emergency.delivered_at
        ? `Recorded ${new Date(emergency.delivered_at).toLocaleString()}`
        : "No delivery confirmation recorded.",
    },
  ]

  return (
    <>
      <div className="fixed inset-0 z-40 bg-black/30" onClick={onClose} />
      <div className="fixed right-0 top-0 z-50 h-screen w-full max-w-[560px] overflow-y-auto bg-white shadow-2xl">
        <div className="flex items-center justify-between border-b border-border p-6">
          <div>
            <h2 className="text-xl font-semibold tracking-tight text-slate-900">Emergency case</h2>
            <p className="mt-1 text-sm text-gray-500">#{emergency.emergency_case_id.slice(0, 8)}</p>
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
                <h3 className="text-lg font-semibold text-slate-900">Operational snapshot</h3>
                <div className="mt-4 grid grid-cols-2 gap-3">
                  {incidentMetrics.map((metric) => (
                    <div key={metric.label} className="rounded-xl border border-slate-200 bg-white p-3">
                      <p className="text-[11px] uppercase tracking-[0.14em] text-slate-500">{metric.label}</p>
                      <p className="mt-1 font-semibold text-slate-900">{metric.value}</p>
                    </div>
                  ))}
                </div>
              </div>
              <EmergencySummary emergency={emergency} />
              <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
                <h3 className="text-lg font-semibold text-slate-900">Workflow status</h3>
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

          {activeTab === "ai" && (
            <AIRecommendation
              emergency={emergency}
              onDispatch={handleRequest}
              actionLabel={requestLabel}
              dispatchDisabled={requestDisabled}
            />
          )}

          {activeTab === "donors" && (
            <DonorComparison
              emergency={emergency}
              onRequestTransfer={handleRequest}
              requestDisabled={requestDisabled}
              requestLabel={requestLabel}
            />
          )}

          {activeTab === "timeline" && <EmergencyTimeline emergency={emergency} />}

          {activeTab === "audit" && (
            <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
              <h3 className="text-lg font-semibold text-slate-900">Recorded workflow milestones</h3>
              <p className="mt-2 text-sm text-slate-600">
                This view uses timestamps persisted on the emergency, transfer and dispatch records. It is not an append-only audit event stream yet.
              </p>
              <div className="mt-4 space-y-3">
                {workflowSteps.filter((step) => !step.detail.startsWith("No ") && !step.detail.includes("not been assigned")).map((step) => (
                  <div key={step.title} className="rounded-xl border border-slate-200 bg-slate-50 p-3">
                    <p className="font-semibold text-slate-900">{step.title}</p>
                    <p className="mt-1 text-sm text-slate-600">{step.detail}</p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        <div className="sticky bottom-0 flex gap-3 border-t border-slate-200 bg-white p-4">
          <Button variant="ghost" className="flex-1" onClick={onClose}>Close</Button>
          <Button
            variant="primary"
            className="flex-1"
            onClick={handleRequest}
            disabled={requestDisabled || isSubmitting}
          >
            {isSubmitting ? "Submitting…" : requestLabel}
          </Button>
        </div>
      </div>

      {showRequestModal && (
        <div className="fixed inset-0 z-[60] flex items-center justify-center bg-black/40 p-4">
          <div className="w-full max-w-md rounded-2xl border border-slate-200 bg-white p-5 shadow-2xl">
            <h3 className="text-lg font-semibold text-slate-900">Create supply transfer requests?</h3>
            <p className="mt-2 text-sm text-slate-600">
              AegisFlow will generate pending transfer legs from ranked eligible donors to cover the remaining quantity where possible. No inventory will be reserved or moved until the destination hospital approves each leg.
            </p>
            <div className="mt-4 flex gap-3">
              <Button variant="ghost" className="flex-1" onClick={() => setShowRequestModal(false)} disabled={isSubmitting}>
                Cancel
              </Button>
              <Button variant="primary" className="flex-1" onClick={confirmRequest} disabled={isSubmitting}>
                {isSubmitting ? "Creating requests…" : "Confirm requests"}
              </Button>
            </div>
          </div>
        </div>
      )}
    </>
  )
}
