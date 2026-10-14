import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { emergencyAPI } from "../services/api"

export function useAllocationPlan(emergencyId?: string) {
  return useQuery({
    queryKey: ["allocation-plan", emergencyId],
    enabled: Boolean(emergencyId),
    queryFn: async () => {
      const response = await emergencyAPI.getAllocation(emergencyId!)
      return response.data
    },
  })
}

export function useAllocationDecision(emergencyId: string) {
  const queryClient = useQueryClient()

  const approve = useMutation({
    mutationFn: (lines: Array<{ allocation_line_id: string; approved_quantity: number }>) =>
      emergencyAPI.approveAllocation(emergencyId, lines),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["allocation-plan", emergencyId] })
      queryClient.invalidateQueries({ queryKey: ["emergencies"] })
    },
  })

  const reject = useMutation({
    mutationFn: () => emergencyAPI.rejectAllocation(emergencyId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["allocation-plan", emergencyId] })
      queryClient.invalidateQueries({ queryKey: ["emergencies"] })
    },
  })

  return { approve, reject }
}