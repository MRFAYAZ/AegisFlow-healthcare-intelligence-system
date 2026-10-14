import { useState, useEffect, useMemo } from "react"
import { useQueryClient } from "@tanstack/react-query"
import { useEmergencies } from "../../hooks/useEmergency"
import { EmergencyBanner } from "./components/EmergencyBanner"
import { EmergencyKPIs } from "./components/EmergencyKPIs"
import { EmergencyCard } from "./components/EmergencyCard"
import { EmergencyDrawer } from "./components/EmergencyDrawer"
import { EmergencyFilters } from "./components/EmergencyFilters"
import { EmergencyMap } from "./components/EmergencyMap"
import { redistributionAPI } from "../../services/api"
import { EmergencyNotifications } from "./components/EmergencyNotifications"

const REFRESH_INTERVAL_MS = 5000

// Extracted outside the component to prevent recreation on every render
const SEVERITY_PRIORITY = {
    EMERGENCY: 5,
    CRITICAL: 4,
    HIGH: 3,
    MEDIUM: 2,
    LOW: 1,
    WARNING: 1,
} as const

export function EmergencyPage() {
    const queryClient = useQueryClient()
    
    // Extracted dataUpdatedAt to show true sync time
    const { data: emergenciesData = [], isLoading, error, dataUpdatedAt } = useEmergencies()
    
    const [selectedEmergencyId, setSelectedEmergencyId] = useState<string | null>(null)
    const [search, setSearch] = useState("")
    const [severity, setSeverity] = useState("ALL")
    const [status, setStatus] = useState("ALL")
    const [currentTime, setCurrentTime] = useState(new Date())

    const emergencies = emergenciesData
    const selectedEmergency =
        emergencies.find((emergency) => emergency.emergency_case_id === selectedEmergencyId) ?? null

    const advanceEmergencyWorkflow = async (emergencyId: string) => {
        try {
            await redistributionAPI.dispatch(emergencyId)
            await queryClient.invalidateQueries({ queryKey: ["emergencies"] })
        } catch (error) {
            console.error("Dispatch request failed", error)
        }
    }

    // 1. Live Clock (Polling is handled inside useEmergencies hook via refetchInterval)
    useEffect(() => {
        const clock = setInterval(() => {
            setCurrentTime(new Date())
        }, 1000)

        return () => clearInterval(clock)
    }, [])

    if (isLoading) {
        return (
            <div className="flex min-h-[400px] flex-col items-center justify-center space-y-4 p-10 text-ink-muted">
                <div className="flex space-x-2">
                    <div className="h-3 w-3 animate-bounce rounded-full bg-slate-400"></div>
                    <div className="h-3 w-3 animate-bounce rounded-full bg-slate-400" style={{ animationDelay: "0.15s" }}></div>
                    <div className="h-3 w-3 animate-bounce rounded-full bg-slate-400" style={{ animationDelay: "0.3s" }}></div>
                </div>
                <div className="text-sm font-medium uppercase tracking-widest text-slate-400">Loading Operations Center</div>
            </div>
        )
    }

    if (error) {
        return (
            <div className="mx-auto mt-10 max-w-2xl rounded-xl border border-red-200 bg-red-50 p-8 text-center shadow-sm">
                <h3 className="text-lg font-bold text-red-800">System Connection Error</h3>
                <p className="mt-2 text-sm text-red-600">
                    Unable to connect to the Emergency Operations Network. Please verify your connection or contact IT support.
                </p>
                <button 
                    onClick={() => queryClient.invalidateQueries({ queryKey: ["emergencies"] })}
                    className="mt-5 rounded-lg bg-red-100 px-4 py-2 text-sm font-semibold text-red-700 transition-colors hover:bg-red-200"
                >
                    Retry Connection
                </button>
            </div>
        )
    }

    const active = emergencies.filter((emergency) => emergency.emergency_status !== "RESOLVED")
    const filtered = active.filter((emergency) => {
        const query = search.trim().toLowerCase()
        const matchesSearch =
            query.length === 0 ||
            [emergency.emergency_case_id, emergency.facility_name, emergency.medicine_name]
                .some((value) => value.toLowerCase().includes(query))
        const matchesSeverity = severity === "ALL" || emergency.severity === severity
        const matchesStatus = status === "ALL" || emergency.emergency_status === status

        return matchesSearch && matchesSeverity && matchesStatus
    })

    // 2. Memoized sorting for performance
    const sortedEmergencies = useMemo(() => {
        return [...filtered].sort(
            (a, b) =>
                (SEVERITY_PRIORITY[b.severity as keyof typeof SEVERITY_PRIORITY] ?? 0) - 
                (SEVERITY_PRIORITY[a.severity as keyof typeof SEVERITY_PRIORITY] ?? 0)
        )
    }, [filtered])

    return (
        <div className="emergency-command-center space-y-6 pb-12">
            <EmergencyBanner activeCount={active.length} />

            {/* Workflow Summary / Header */}
            <div className="emergency-overview panel">
                <div className="flex justify-between items-start">
                    <div>
                        <div className="section-kicker">Network response control</div>
                        <h3 className="text-2xl font-semibold tracking-tight text-ink">Emergency Operations Center</h3>
                        <p className="text-sm text-ink-muted whitespace-pre-line mt-1">
                            Live shortage detection, explainable donor matching, and coordinated redistribution across the healthcare network.
                        </p>
                    </div>
                    <div className="text-right">
                        <div className="text-sm font-semibold text-ink">{currentTime.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</div>
                        <div className="text-xs text-emerald-600 flex items-center justify-end gap-1.5 mt-1">
                            <span className="relative flex h-2 w-2">
                                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                                <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
                            </span>
                            {/* Uses actual fetch time from React Query */}
                            Live · Synced {dataUpdatedAt ? new Date(dataUpdatedAt).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : '...'}
                        </div>
                        <div className="text-xs text-ink-faint mt-1">Auto refresh every {REFRESH_INTERVAL_MS / 1000} seconds</div>
                    </div>
                </div>
                
                {/* 3. High-Level Workflow Cards */}
                <div className="workflow-rail mt-6">
                    <WorkflowCard 
                        title="Source matching" 
                        value={emergencies.filter(e => e.transfer_status === "MATCHING").length} 
                        color="blue" 
                    />
                    <WorkflowCard 
                        title="Awaiting Approval" 
                        value={emergencies.filter(e => e.transfer_status === "PENDING").length} 
                        color="amber" 
                    />
                    <WorkflowCard 
                        title="In Transit" 
                        value={emergencies.filter(e => e.transfer_status === "IN_TRANSIT").length} 
                        color="green" 
                    />
                    <WorkflowCard 
                        title="Completed" 
                        value={emergencies.filter(e => e.transfer_status === "COMPLETED").length} 
                        color="emerald" 
                    />
                </div>
            </div>

            <EmergencyKPIs emergencies={emergencies} />
            
            <div className="situation-grid">
                <section>
                    <div className="section-heading"><div><div className="section-kicker">Situation awareness</div><h2>Healthcare network</h2></div><span className="section-meta">{filtered.length} active incidents</span></div>
                    <EmergencyMap emergencies={filtered} />
                </section>
                <section>
                    <div className="section-heading"><div><div className="section-kicker">Operational signal</div><h2>Live operations feed</h2></div><span className="section-meta">Auto-updating</span></div>
                    <EmergencyNotifications emergencies={emergencies} />
                </section>
            </div>
            
            <div className="incident-workbench mt-8">
                <div className="section-heading"><div><div className="section-kicker">Response queue</div><h2>Incident explorer</h2></div><span className="section-meta">{sortedEmergencies.length} showing</span></div>
                <EmergencyFilters
                    search={search}
                    setSearch={setSearch}
                    severity={severity}
                    setSeverity={setSeverity}
                    status={status}
                    setStatus={setStatus}
                />

                {sortedEmergencies.length === 0 ? (
                    <div className="mt-6 rounded-xl border border-dashed border-border-strong bg-surface-base p-8 text-center text-ink-muted">
                        <p className="font-medium text-ink">No active incidents match the selected filters.</p>
                        <p className="mt-1 text-sm">Try changing the search, severity or status filters.</p>
                    </div>
                ) : (
                    <div className="mt-6 grid grid-cols-1 gap-6 lg:grid-cols-2 xl:grid-cols-3">
                        {sortedEmergencies.map((emergency) => (
                            <EmergencyCard
                                key={emergency.emergency_case_id}
                                emergency={emergency}
                                onView={(selected) => setSelectedEmergencyId(selected.emergency_case_id)}
                            />
                        ))}
                    </div>
                )}
            </div>

            <EmergencyDrawer
                emergency={selectedEmergency}
                open={selectedEmergency !== null}
                onClose={() => setSelectedEmergencyId(null)}
                onAdvanceWorkflow={advanceEmergencyWorkflow}
            />

           {/* 5. Enterprise Footer */}
            <div className="rounded-xl border border-border-strong bg-surface-strong text-ink-muted p-4 shadow-sm mt-8">
                <div className="flex flex-col md:flex-row justify-between items-center text-sm font-medium">
                    <div className="text-white font-semibold flex items-center gap-2">
                        <span>AegisFlow Emergency Operations Center</span>
                    </div>
                    <div className="text-ink-faint">Powered by React, FastAPI, PostgreSQL and PostGIS</div>
                    <div className="flex items-center gap-4 mt-2 md:mt-0">
                        <div className="flex items-center gap-1.5 text-ink-faint text-xs uppercase tracking-wider">
                            <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8V7a4 4 0 00-8 0v4h8z" />
                            </svg>
                            Encrypted
                        </div>
                        <div className="flex items-center gap-2 text-emerald-400">
                            <span className="relative flex h-2 w-2">
                                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                                <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
                            </span>
                            All Systems Operational
                        </div>
                    </div>
                </div>
            </div>
        </div> 
    )
}

// --- Helper Components for the Dashboard UI ---
// Note: As suggested in the review, for a fully mature architecture, 
// you would eventually extract `WorkflowCard` into `components/WorkflowCard.tsx`.

function WorkflowCard({ title, value, color }: { title: string, value: number, color: 'blue' | 'amber' | 'green' | 'emerald' }) {
    const colorStyles = {
        blue: "bg-blue-50 border-blue-200 text-blue-900",
        amber: "bg-amber-50 border-amber-200 text-amber-900",
        green: "bg-green-50 border-green-200 text-green-900",
        emerald: "bg-emerald-50 border-emerald-200 text-emerald-900",
    }
    const labelStyles = {
        blue: "text-blue-700",
        amber: "text-amber-700",
        green: "text-green-700",
        emerald: "text-emerald-700",
    }

    return (
        <div className={`rounded-xl border p-4 shadow-sm ${colorStyles[color]}`}>
            <p className={`text-xs uppercase tracking-wider font-semibold ${labelStyles[color]}`}>
                {title}
            </p>
            <p className="mt-1 text-3xl font-bold">{value}</p>
        </div>
    )
}