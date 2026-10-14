import { useState, useEffect } from "react"
import { useQueryClient } from "@tanstack/react-query"
import { useEmergencies } from "../../hooks/useEmergency"
import { useFacilities } from "../../hooks/useFacilities"
import { EmergencyBanner } from "./components/EmergencyBanner"
import { EmergencyKPIs } from "./components/EmergencyKPIs"
import { EmergencyCard } from "./components/EmergencyCard"
import { EmergencyDrawer } from "./components/EmergencyDrawer"
import { EmergencyFilters } from "./components/EmergencyFilters"
import { EmergencyMap } from "./components/EmergencyMap"
import { redistributionAPI } from "../../services/api"

type FacilityRecord = Record<string, unknown>

function isRecord(value: unknown): value is FacilityRecord {
    return typeof value === "object" && value !== null
}

export function EmergencyPage() {
    const queryClient = useQueryClient()
    const { data: emergenciesData = [], isLoading, error } = useEmergencies()
    const { data: facilityData = [] } = useFacilities()
    const [selectedEmergencyId, setSelectedEmergencyId] = useState<string | null>(null)
    const [search, setSearch] = useState("")
    const [severity, setSeverity] = useState("ALL")
    const [status, setStatus] = useState("ALL")

    const emergencies = emergenciesData
    const selectedEmergency =
        emergencies.find((emergency) => emergency.emergency_case_id === selectedEmergencyId) ?? null

    const facilityRecords: FacilityRecord[] = Array.isArray(facilityData)
        ? facilityData.filter(isRecord)
        : []
    const activeFacilityRecords = facilityRecords.filter((facility) => facility.is_active !== false)
    const countFacilityType = (types: string[]) =>
        activeFacilityRecords.filter((facility) =>
            types.includes(String(facility.facility_type ?? "").toUpperCase())
        ).length
    const facilitiesWithCoordinates = activeFacilityRecords.filter((facility) => {
        const latitude = Number(facility.latitude)
        const longitude = Number(facility.longitude)
        return Number.isFinite(latitude) && latitude >= -90 && latitude <= 90
            && Number.isFinite(longitude) && longitude >= -180 && longitude <= 180
    }).length

    const advanceEmergencyWorkflow = async (emergencyId: string) => {
        try {
            await redistributionAPI.dispatch(emergencyId)
            await queryClient.invalidateQueries({ queryKey: ["emergencies"] })
        } catch {
            // Surface the error in the UI rather than silently pretending dispatch succeeded.
            window.alert("The transfer request could not be submitted. Check the current transfer state and try again.")
        }
    }

    if (isLoading) {
        return <div className="p-10">Loading Emergency Center...</div>
    }

    if (error) {
        return <div className="p-10 text-red-600">Failed to load emergencies.</div>
    }

    const active = emergencies.filter(
        (emergency) => emergency.emergency_status !== "RESOLVED" && emergency.emergency_status !== "CLOSED"
    )
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

    const inWorkflow = emergencies.filter((emergency) =>
        ["PENDING", "APPROVED", "IN_TRANSIT"].includes(emergency.transfer_status ?? "")
    )
    const matchScores = emergencies
        .map((emergency) => emergency.match_score)
        .filter((score): score is number => score !== null && Number.isFinite(Number(score)))
        .map(Number)
    const operationsSummary = {
        activeEmergencies: active.length,
        facilitiesWithTransfers: new Set(inWorkflow.map((emergency) => emergency.facility_id)).size,
        pendingApprovals: emergencies.filter((emergency) => emergency.transfer_status === "PENDING").length,
        hospitals: countFacilityType(["HOSPITAL"]),
        shops: countFacilityType(["MEDICAL_SHOP"]),
        suppliers: countFacilityType(["SUPPLIER"]),
        warehouses: countFacilityType(["WAREHOUSE"]),
        dispatchQueue: emergencies.filter((emergency) =>
            emergency.transfer_status === "APPROVED" || emergency.transfer_status === "IN_TRANSIT"
        ).length,
        averageMatch: matchScores.length
            ? matchScores.reduce((sum, score) => sum + score, 0) / matchScores.length
            : null,
        recordsWithTransfers: emergencies.filter((emergency) => Boolean(emergency.transfer_id)).length,
        facilitiesWithCoordinates,
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
                <div className="flex items-start justify-between">
                    <div>
                        <h3 className="text-xl font-semibold">Emergency Operations Center</h3>
                        <p className="text-sm text-slate-500">Shortage response with explainable donor matching</p>
                    </div>
                    <div className="text-right">
                        <div className="text-sm font-semibold">{currentTime.toLocaleTimeString()}</div>
                        <div className="text-xs text-slate-500">Emergency data refreshes every 5 seconds</div>
                    </div>
                </div>

                <div className="mt-4 grid grid-cols-2 gap-4 md:grid-cols-4 xl:grid-cols-4">
                    <SummaryMetric label="Active Emergencies" value={operationsSummary.activeEmergencies} />
                    <SummaryMetric label="Facilities with Transfer Activity" value={operationsSummary.facilitiesWithTransfers} />
                    <SummaryMetric label="Pending Approvals" value={operationsSummary.pendingApprovals} />
                    <SummaryMetric label="Dispatch Queue" value={operationsSummary.dispatchQueue} />
                </div>
                <div className="mt-4 grid grid-cols-2 gap-4 md:grid-cols-4">
                    <SummaryMetric label="Registered Hospitals" value={operationsSummary.hospitals} />
                    <SummaryMetric label="Registered Medical Shops" value={operationsSummary.shops} />
                    <SummaryMetric label="Registered Suppliers" value={operationsSummary.suppliers} />
                    <SummaryMetric label="Registered Warehouses" value={operationsSummary.warehouses} />
                </div>
                <div className="mt-4 grid grid-cols-2 gap-4 md:grid-cols-3">
                    <SummaryMetric label="Average Match Score" value={operationsSummary.averageMatch === null ? "—" : `${operationsSummary.averageMatch.toFixed(1)} / 100`} />
                    <SummaryMetric label="Emergency Records with Transfer" value={operationsSummary.recordsWithTransfers} />
                    <SummaryMetric label="Geocoded Active Facilities" value={operationsSummary.facilitiesWithCoordinates} />
                </div>
                <p className="mt-3 text-xs text-slate-500">
                    Counts are derived from the current API response. Response-time, notification and delivery-success KPIs are not shown until backed by recorded events.
                </p>
            </div>
            <EmergencyKPIs emergencies={emergencies} />
            <EmergencyMap />
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

function SummaryMetric({ label, value }: { label: string; value: string | number }) {
    return (
        <div className="rounded-xl bg-slate-50 p-3">
            <p className="text-xs uppercase tracking-[0.12em] text-slate-500">{label}</p>
            <p className="mt-1 text-2xl font-semibold text-slate-900">{value}</p>
        </div>
    )
}
