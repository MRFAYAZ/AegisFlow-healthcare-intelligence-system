import { useQuery } from "@tanstack/react-query"
import { emergencyAPI } from "../services/api"
import type { Emergency } from "../types/emergency"

export function useEmergencies() {

    return useQuery<Emergency[]>({

        queryKey: ["emergencies"],

        queryFn: async () => {

            const response =
                await emergencyAPI.getAll()

            return response.data
        }

    })

}

export function useEmergencyDashboard() {

    return useQuery({

        queryKey: ["emergencies"],

        queryFn: async () => {

            const response =
                await emergencyAPI.getAll()

            return response.data
        },
        staleTime: 0,
        refetchInterval: 5000,
        refetchOnWindowFocus: true
    })

}