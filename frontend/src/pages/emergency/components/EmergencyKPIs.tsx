import { KPICard } from "../../../components/ui/KPICard"
import type { Emergency } from "../../../types/emergency"

interface Props {
    emergencies: Emergency[]
}

export function EmergencyKPIs({

    emergencies

}: Props) {

    const emergencyCount =
        emergencies.filter(
            e => e.severity === "EMERGENCY"
        ).length

    const criticalCount =
        emergencies.filter(
            e => e.severity === "CRITICAL"
        ).length

    const matchingCount =
        emergencies.filter(
            e => e.emergency_status === "MATCHING"
        ).length

    return (

        <div className="grid grid-cols-4 gap-4">

            <KPICard

                label="Total Emergencies"

                value={emergencies.length}

                sub="Detected by AI"

                color="red"

            />

            <KPICard

                label="Emergency"

                value={emergencyCount}

                sub="Immediate response"

                color="red"

            />

            <KPICard

                label="Critical"

                value={criticalCount}

                sub="Needs monitoring"

                color="orange"

            />

            <KPICard

                label="Matching"

                value={matchingCount}

                sub="Finding donors"

                color="blue"

            />

        </div>

    )

}