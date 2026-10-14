import { useQuery } from "@tanstack/react-query"
import { emergencyAPI } from "../services/api"

export function useEmergencyMatches(emergencyId?: string) {
  return useQuery({
    queryKey: ["matches", emergencyId],
    enabled: !!emergencyId,
    queryFn: async () => {
      const res = await emergencyAPI.getMatches(emergencyId!)
      return res.data
    },
  })
}