import { useMemo } from "react"
import { useTransfers } from "./useTransfers"
import type { Transfer } from "../types/transfer"

export function useEmergencyTransfer(emergencyId?: string) {
    const { data: transfers = [], isLoading } = useTransfers()

    const transfer = useMemo(() => {
        if (!emergencyId) return null

        return transfers.find((t: Transfer) =>
            (t as Transfer & { to_facility_id?: string }).to_facility_id === emergencyId ||
            (t as Transfer & { emergency_case_id?: string }).emergency_case_id === emergencyId
        )
    }, [transfers, emergencyId])

    return {
        transfer,
        isLoading,
    }
}