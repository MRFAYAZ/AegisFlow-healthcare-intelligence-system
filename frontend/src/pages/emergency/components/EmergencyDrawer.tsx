import { useState } from "react"
import { X } from "lucide-react"
import { Badge } from "../../../components/ui/Badge"
import { Button } from "../../../components/ui/Button"
import type { Emergency } from "../../../types/emergency"
import { EmergencySummary } from "./EmergencySummary"
import { EmergencyTimeline } from "./EmergencyTimeline"
import { AIRecommendation } from "./AIRecommendation"
import { AllocationDecisionCenter } from "./AllocationDecisionCenter"
import { EmergencyWorkflow } from "./EmergencyWorkflow"
import { DispatcherCard } from "./DispatcherCard"

type DrawerTab = "overview" | "decision" | "operations" | "timeline"

interface Props {
  emergency: Emergency | null
  open: boolean
  onClose: () => void
  onAdvanceWorkflow: (emergencyId: string) => void
}

const tabs: Array<{ key: DrawerTab; label: string }> = [
  { key: "overview", label: "Overview" },
  { key: "decision", label: "Decision Center" }, 
  { key: "operations", label: "Operations" },
  { key: "timeline", label: "Timeline" },
]

// Helper to generate dynamic timestamps based on the emergency trigger time
function getRelativeTime(baseDate: string | Date | undefined, minutesToAdd: number) {
  if (!baseDate) return "Pending"
  const date = new Date(baseDate)
  date.setMinutes(date.getMinutes() + minutesToAdd)
  return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}

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

  // Workflow-aware Action Button Logic
  const dispatchLabel = !hasRecommendation
    ? "Generate AI Recommendation"
    : emergency?.transfer_status === "PENDING"
      ? "Awaiting Hospital Approval"
      : emergency?.transfer_status === "APPROVED"
        ? "Assign Dispatcher"
        : emergency?.transfer_status === "IN_TRANSIT"
          ? "Track Shipment"
          : emergency?.transfer_status === "COMPLETED"
            ? "View Report"
            : "Notify Hospital"

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

  // Dynamic Operational Workflow substituting hardcoded audit logs
  const baseTime = emergency.triggered_at || new Date().toISOString()
  const operationsLog = [
    { time: getRelativeTime(baseTime, 0), title: "Emergency Triggered", detail: "Shortage detected in inventory" },
    { time: getRelativeTime(baseTime, 2), title: "Source matching completed", detail: `Top ${Math.max(3, emergency.alternative_donors ?? 5)} donor candidates evaluated` },
    { time: getRelativeTime(baseTime, 5), title: "Hospital Notified", detail: "Recommendation queued for admin review" },
    { time: emergency.transfer_status === "IN_TRANSIT" || emergency.transfer_status === "COMPLETED" ? getRelativeTime(baseTime, 12) : "--:--", title: "Dispatcher Assigned", detail: emergency.transfer_status === "IN_TRANSIT" || emergency.transfer_status === "COMPLETED" ? "Vehicle dispatched" : "Awaiting assignment" },
    { time: emergency.transfer_status === "COMPLETED" ? getRelativeTime(baseTime, 45) : "--:--", title: "Delivered", detail: emergency.transfer_status === "COMPLETED" ? "Transfer completed successfully" : "Pending transit" },
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
          <Button variant="ghost" onClick={onClose} aria-label="Close emergency details"><X size={16} aria-hidden="true" /></Button>
        </div>

        <div className="border-b border-border px-6 py-3">
          <div className="flex flex-wrap gap-2">
            {tabs.map((tab) => (
              <button
                key={tab.key}
                type="button"
                className={`rounded-full px-3 py-1.5 text-sm font-medium transition-colors ${activeTab === tab.key ? "bg-slate-900 text-white" : "bg-slate-100 text-slate-600 hover:bg-slate-200"}`}
                onClick={() => setActiveTab(tab.key)}
              >
                {tab.label}
              </button>
            ))}
          </div>
        </div>

        <div className="space-y-6 p-6">
          
          {/* 1. Overview Tab */}
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
              <EmergencyWorkflow emergency={emergency}/>
            </>
          )}

          {/* 2. Decision Center Tab */}
          {activeTab === "decision" && (
             <div className="space-y-6">
               <AllocationDecisionCenter emergency={emergency} />
               <AIRecommendation 
                 emergency={emergency} 
                 onDispatch={handleDispatch} 
                 actionLabel={dispatchLabel} 
                 dispatchDisabled={!hasRecommendation} 
               />
             </div>
          )}

          {/* 3. Operations Tab */}
          {activeTab === "operations" && (
            <div className="space-y-6">
              <DispatcherCard emergency={emergency} />
              <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
                <h3 className="text-lg font-semibold text-slate-900">Operational Log</h3>
                <p className="text-sm text-slate-500 mb-4">Live tracking of automated and manual interventions.</p>
                <div className="space-y-3">
                  {operationsLog.map((entry, index) => (
                    <div key={index} className="rounded-xl border border-slate-200 bg-slate-50 p-3 flex gap-4">
                      <div className="flex flex-col items-center pt-1 w-12">
                         <span className={`text-xs font-bold ${entry.time === "--:--" ? "text-slate-400" : "text-blue-700"}`}>{entry.time}</span>
                      </div>
                      <div className="flex-1 border-l-2 border-slate-200 pl-4">
                        <p className={`font-semibold ${entry.time === "--:--" ? "text-slate-500" : "text-slate-900"}`}>{entry.title}</p>
                        <p className="mt-1 text-sm text-slate-600">{entry.detail}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* 4. Timeline Tab */}
          {activeTab === "timeline" && <EmergencyTimeline emergency={emergency} />}

        </div>

        {/* Floating Action Bar */}
        <div className="sticky bottom-0 flex gap-3 border-t border-slate-200 bg-white p-4 shadow-[0_-4px_6px_-1px_rgba(0,0,0,0.05)]">
          <Button variant="ghost" className="flex-1" onClick={onClose}>Close</Button>
          <Button 
            variant="primary" 
            className="flex-1 shadow-md" 
            onClick={handleDispatch} 
            disabled={!hasRecommendation && emergency.transfer_status !== "PENDING"}
          >
            {dispatchLabel}
          </Button>
        </div>
      </div>

      {showDispatchModal && (
        <div className="fixed inset-0 z-[60] flex items-center justify-center bg-black/40 p-4 backdrop-blur-sm">
          <div className="w-full max-w-md rounded-2xl border border-slate-200 bg-white p-5 shadow-2xl">
            <h3 className="text-lg font-semibold text-slate-900">Confirm Action</h3>
            <p className="mt-2 text-sm text-slate-600">
              {emergency.transfer_status === "PENDING" 
                ? "This will manually approve the recommendation on behalf of the hospital." 
                : "This sends the recommendation to the hospital admin for approval before the dispatcher is assigned."}
            </p>
            <div className="mt-5 flex gap-3">
              <Button variant="ghost" className="flex-1" onClick={() => setShowDispatchModal(false)}>
                Cancel
              </Button>
              <Button variant="primary" className="flex-1 shadow-sm" onClick={confirmDispatch}>
                Confirm
              </Button>
            </div>
          </div>
        </div>
      )}
    </>
  )
}