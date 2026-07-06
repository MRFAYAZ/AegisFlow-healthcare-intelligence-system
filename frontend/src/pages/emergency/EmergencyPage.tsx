import { useState, useEffect } from "react"
import { useQueryClient } from "@tanstack/react-query"
import { useEmergencies } from "../../hooks/useEmergency"
import { EmergencyBanner } from "./components/EmergencyBanner"
import { EmergencyKPIs } from "./components/EmergencyKPIs"
import { EmergencyCard } from "./components/EmergencyCard"
import { EmergencyDrawer } from "./components/EmergencyDrawer"
import { EmergencyFilters } from "./components/EmergencyFilters"
import { EmergencyMap } from "./components/EmergencyMap"
import { redistributionAPI } from "../../services/api"

export function EmergencyPage() {
    const queryClient = useQueryClient()
    const { data: emergenciesData = [], isLoading, error } = useEmergencies()
    const [selectedEmergencyId, setSelectedEmergencyId] = useState<string | null>(null)
    const [search, setSearch] = useState("")
    const [severity, setSeverity] = useState("ALL")
    const [status, setStatus] = useState("ALL")

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

    if (isLoading) {
        return <div className="p-10">Loading Emergency Center...</div>
    }

    if (error) {
        return <div className="p-10 text-red-600">Failed to load emergencies.</div>
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

    const operationsSummary = {
        activeEmergencies: active.length,
        hospitalsResponding: emergencies.filter((emergency) => emergency.transfer_status === "PENDING" || emergency.transfer_status === "APPROVED" || emergency.transfer_status === "IN_TRANSIT").length,
        pendingApprovals: emergencies.filter((emergency) => emergency.transfer_status === "PENDING").length,
        hospitalsOnline: 14,
        shopsOnline: 8,
        suppliersOnline: 6,
        pendingNotifications: 11,
        dispatchQueue: emergencies.filter((emergency) => emergency.transfer_status === "APPROVED" || emergency.transfer_status === "IN_TRANSIT").length,
        averageResponseTime: 16,
        averageMatch: emergencies.reduce((sum, emergency) => sum + Number(emergency.match_score ?? 0), 0) / (emergencies.length || 1),
        averageEta: emergencies.reduce((sum, emergency) => sum + Number(emergency.estimated_eta_minutes ?? 0), 0) / (emergencies.length || 1),
        dispatchSuccess: 98,
    }

    const [currentTime, setCurrentTime] = useState(new Date())
    
    useEffect(() => {
        const timer = setInterval(() => {
            setCurrentTime(new Date())
        }, 1000)

        return () => clearInterval(timer)
    }, [])

    return (
        <div className="space-y-6">
            <EmergencyBanner activeCount={active.length} />
            <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
                <div className="flex justify-between items-start">
                    <div>
                        <h3 className="text-xl font-semibold">Emergency Operations Center</h3>
                        <p className="text-sm text-slate-500">AI Powered Healthcare Redistribution Network</p>
                    </div>
                    <div className="text-right">
                        <div className="text-sm font-semibold"> {currentTime.toLocaleTimeString()}</div>
                        <div className="text-xs text-slate-500">Auto Refresh * 5 sec</div>
                    </div>
                </div>
                
                <div className="mt-4 grid grid-cols-2 gap-4 md:grid-cols-4 xl:grid-cols-8">
                    <div className="rounded-xl bg-slate-50 p-3">
                        <p className="text-xs uppercase tracking-[0.2em] text-slate-500">Active Emergencies</p>
                        <p className="mt-1 text-2xl font-semibold text-slate-900">{operationsSummary.activeEmergencies}</p>
                    </div>
                    <div className="rounded-xl bg-slate-50 p-3">
                        <p className="text-xs uppercase tracking-[0.2em] text-slate-500">Hospitals Responding</p>
                        <p className="mt-1 text-2xl font-semibold text-slate-900">{operationsSummary.hospitalsResponding}</p>
                    </div>
                    <div className="rounded-xl bg-slate-50 p-3">
                        <p className="text-xs uppercase tracking-[0.2em] text-slate-500">Pending Approvals</p>
                        <p className="mt-1 text-2xl font-semibold text-slate-900">{operationsSummary.pendingApprovals}</p>
                    </div>
                    <div className="rounded-xl bg-slate-50 p-3">
                        <p className="text-xs uppercase tracking-[0.2em] text-slate-500">Hospitals Online</p>
                        <p className="mt-1 text-2xl font-semibold text-slate-900">{operationsSummary.hospitalsOnline}</p>
                    </div>
                    <div className="rounded-xl bg-slate-50 p-3">
                        <p className="text-xs uppercase tracking-[0.2em] text-slate-500">Medical Shops Online</p>
                        <p className="mt-1 text-2xl font-semibold text-slate-900">{operationsSummary.shopsOnline}</p>
                    </div>
                    <div className="rounded-xl bg-slate-50 p-3">
                        <p className="text-xs uppercase tracking-[0.2em] text-slate-500">Suppliers Online</p>
                        <p className="mt-1 text-2xl font-semibold text-slate-900">{operationsSummary.suppliersOnline}</p>
                    </div>
                    <div className="rounded-xl bg-slate-50 p-3">
                        <p className="text-xs uppercase tracking-[0.2em] text-slate-500">Pending Notifications</p>
                        <p className="mt-1 text-2xl font-semibold text-slate-900">{operationsSummary.pendingNotifications}</p>
                    </div>
                    <div className="rounded-xl bg-slate-50 p-3">
                        <p className="text-xs uppercase tracking-[0.2em] text-slate-500">Dispatch Queue</p>
                        <p className="mt-1 text-2xl font-semibold text-slate-900">{operationsSummary.dispatchQueue}</p>
                    </div>
                </div>
                <div className="mt-4 grid grid-cols-2 gap-4 md:grid-cols-3">
                    <div className="rounded-xl bg-slate-50 p-3">
                        <p className="text-xs uppercase tracking-[0.2em] text-slate-500">Average AI Match</p>
                        <p className="mt-1 text-2xl font-semibold text-slate-900">{operationsSummary.averageMatch.toFixed(0)}%</p>
                    </div>
                    <div className="rounded-xl bg-slate-50 p-3">
                        <p className="text-xs uppercase tracking-[0.2em] text-slate-500">Average ETA</p>
                        <p className="mt-1 text-2xl font-semibold text-slate-900">{operationsSummary.averageEta.toFixed(0)} min</p>
                    </div>
                    <div className="rounded-xl bg-slate-50 p-3">
                        <p className="text-xs uppercase tracking-[0.2em] text-slate-500">Average Response Time</p>
                        <p className="mt-1 text-2xl font-semibold text-slate-900">{operationsSummary.averageResponseTime} min</p>
                    </div>
                </div>
            </div>
            <EmergencyKPIs emergencies={emergencies} />
            <EmergencyMap
                emergencies={filtered}
            />
            <EmergencyDrawer
                emergency={selectedEmergency}
                open={selectedEmergency !== null}
                onClose={() => setSelectedEmergencyId(null)}
                onAdvanceWorkflow={advanceEmergencyWorkflow}
            />
            <EmergencyFilters
                search={search}
                setSearch={setSearch}
                severity={severity}
                setSeverity={setSeverity}
                status={status}
                setStatus={setStatus}
            />
            {filtered.length === 0 ? (
                <div className="rounded-xl border border-dashed border-border bg-white p-8 text-center text-ink-muted">
                    No matching emergencies found.
                </div>
            ) : (
                <div className="grid grid-cols-1 gap-6 lg:grid-cols-2 xl:grid-cols-3">
                    {filtered.map((emergency) => (
                        <EmergencyCard
                            key={emergency.emergency_case_id}
                            emergency={emergency}
                            onView={(selected) => setSelectedEmergencyId(selected.emergency_case_id)}
                        />
                    ))}
                </div>
            )}
        </div>
    )
}