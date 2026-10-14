import { useState } from "react"
import { useLocation, useNavigate } from "react-router-dom"
import { useEmergencies } from "../../hooks/useEmergency"
import { useCurrentUser } from "../../hooks/useCurrentUser"

const pageTitles: Record<string, string> = {
  "/dashboard": "Command center",
  "/emergency": "Emergency operations",
  "/inventory": "Inventory management",
  "/shortage": "Shortage intelligence",
  "/transfers": "Transfer control center",
  "/analytics": "Analytics & intelligence",
  "/map": "Geospatial map",
  "/shop": "Medical shop",
}

const severityWeight: Record<string, number> = {
  EMERGENCY: 5,
  CRITICAL: 4,
  WARNING: 3,
  MEDIUM: 2,
  LOW: 1,
}

function formatTime(value: string) {
  const parsed = new Date(value)
  return Number.isNaN(parsed.getTime()) ? "Time not recorded" : parsed.toLocaleString()
}

export function Topbar() {
  const { pathname } = useLocation()
  const navigate = useNavigate()
  const [notifsOpen, setNotifsOpen] = useState(false)
  const { data: user } = useCurrentUser()
  const canViewNetworkEmergencies = ["system_admin", "emergency_operator", "hospital_admin"].includes(user?.role ?? "")
  const { data: emergencies = [], isLoading, isError } = useEmergencies(canViewNetworkEmergencies)

  const activeEmergencies = emergencies
    .filter((emergency) => emergency.emergency_status !== "RESOLVED" && emergency.emergency_status !== "CLOSED")
    .sort((a, b) => (severityWeight[b.severity] ?? 0) - (severityWeight[a.severity] ?? 0))
  const criticalCount = activeEmergencies.filter(
    (emergency) => emergency.severity === "EMERGENCY" || emergency.severity === "CRITICAL"
  ).length
  const title = pageTitles[pathname] || "AegisFlow"

  const systemLabel = !canViewNetworkEmergencies
    ? "Facility scope"
    : isLoading
      ? "Checking operations"
      : isError
        ? "Status unavailable"
        : criticalCount > 0
          ? `${criticalCount} critical case${criticalCount === 1 ? "" : "s"}`
          : activeEmergencies.length > 0
            ? `${activeEmergencies.length} active case${activeEmergencies.length === 1 ? "" : "s"}`
            : "No active emergencies"

  const systemTone = !canViewNetworkEmergencies || isLoading || isError
    ? "bg-slate-50 border-slate-200 text-slate-600"
    : criticalCount > 0
      ? "bg-red-50 border-red-200 text-red-700"
      : activeEmergencies.length > 0
        ? "bg-amber-50 border-amber-200 text-amber-700"
        : "bg-green-50 border-green-200 text-green-700"

  return (
    <header className="h-12 bg-white border-b border-border flex items-center px-5 gap-3 flex-shrink-0">
      <div className="text-[14px] font-semibold text-ink flex-1">{title}</div>

      <div className="flex items-center gap-2 bg-surface-muted border border-border rounded px-3 py-1.5 w-48 text-ink-faint text-[12px]">
        <span className="text-[13px]">⌕</span>
        Search the workspace
      </div>

      <div className="relative">
        <button
          aria-label="View operational alerts"
          className="w-8 h-8 rounded border border-border bg-white flex items-center justify-center text-ink-muted hover:bg-surface-muted relative"
          onClick={() => setNotifsOpen((previous) => !previous)}
        >
          🔔
          {criticalCount > 0 && (
            <span className="absolute -top-1 -right-1 min-w-4 h-4 rounded-full bg-red-600 text-white text-[9px] flex items-center justify-center px-1">
              {criticalCount > 99 ? "99+" : criticalCount}
            </span>
          )}
        </button>

        {notifsOpen && (
          <div className="absolute top-10 right-0 w-80 bg-white border border-border rounded-xl shadow-lg z-50">
            <div className="flex items-center justify-between px-3 py-2.5 border-b border-border">
              <div>
                <div className="text-[12px] font-semibold text-ink">Operational alerts</div>
                <div className="text-[10px] text-ink-faint">
                  {canViewNetworkEmergencies ? `${activeEmergencies.length} active emergency case(s)` : "Facility-scoped workspace"}
                </div>
              </div>
              {canViewNetworkEmergencies && (
                <button
                  onClick={() => { setNotifsOpen(false); navigate("/emergency") }}
                  className="text-[11px] text-blue-600"
                >
                  Open EOC
                </button>
              )}
            </div>

            {!canViewNetworkEmergencies && (
              <div className="px-4 py-5 text-[11px] text-ink-muted">
                Network emergency alerts are limited by your current role.
              </div>
            )}

            {canViewNetworkEmergencies && isLoading && (
              <div className="px-4 py-5 text-[11px] text-ink-muted">Loading active emergency records…</div>
            )}

            {canViewNetworkEmergencies && isError && (
              <div role="alert" className="px-4 py-5 text-[11px] text-red-700">
                Emergency alerts could not be loaded from the backend.
              </div>
            )}

            {canViewNetworkEmergencies && !isLoading && !isError && activeEmergencies.length === 0 && (
              <div className="px-4 py-5 text-[11px] text-ink-muted">No active emergency cases in your authorized scope.</div>
            )}

            {canViewNetworkEmergencies && !isLoading && !isError && activeEmergencies.slice(0, 5).map((emergency) => (
              <button
                key={emergency.emergency_case_id}
                className="w-full text-left flex gap-2.5 px-3 py-2.5 border-b border-border last:border-b-0 hover:bg-surface-muted"
                onClick={() => { setNotifsOpen(false); navigate("/emergency") }}
              >
                <div className={`w-1.5 h-1.5 rounded-full flex-shrink-0 mt-1.5 ${emergency.severity === "EMERGENCY" || emergency.severity === "CRITICAL" ? "bg-red-600" : "bg-amber-500"}`} />
                <div className="min-w-0">
                  <div className="text-[11px] text-ink leading-snug font-medium">
                    {emergency.medicine_name} — {emergency.facility_name}
                  </div>
                  <div className="text-[10px] text-ink-faint mt-0.5">
                    {emergency.severity} · {emergency.emergency_status.replaceAll("_", " ")}
                  </div>
                  <div className="text-[10px] text-ink-faint mt-0.5">{formatTime(emergency.triggered_at)}</div>
                </div>
              </button>
            ))}
          </div>
        )}
      </div>

      <button
        aria-label="Settings"
        className="w-8 h-8 rounded border border-border bg-white flex items-center justify-center text-ink-muted hover:bg-surface-muted"
        onClick={() => navigate("/dashboard")}
      >
        ⚙
      </button>

      <div className={`flex items-center gap-1.5 px-3 py-1 rounded-full border text-[11px] font-medium ${systemTone}`}>
        <span className={`w-1.5 h-1.5 rounded-full inline-block ${criticalCount > 0 && canViewNetworkEmergencies ? "bg-red-500" : activeEmergencies.length > 0 && canViewNetworkEmergencies ? "bg-amber-500" : "bg-current"}`} />
        {systemLabel}
      </div>
    </header>
  )
}
