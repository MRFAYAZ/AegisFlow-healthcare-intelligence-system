import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { dispatchAPI } from '../services/api'

export function useDispatchDashboard() {
  return useQuery({
    queryKey: ['dispatch-dashboard'],
    queryFn: async () => (await dispatchAPI.getDashboard()).data,
    refetchInterval: 10000,
  })
}

function invalidateDispatchQueries(queryClient: ReturnType<typeof useQueryClient>) {
  queryClient.invalidateQueries({ queryKey: ['dispatch-dashboard'] })
  queryClient.invalidateQueries({ queryKey: ['redistribution'] })
}

export function useAssignDispatch() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ transferId, transportType, vehicleReference }: {
      transferId: string
      transportType: string
      vehicleReference?: string
    }) => dispatchAPI.assign(transferId, {
      transport_type: transportType,
      vehicle_reference: vehicleReference,
    }),
    onSuccess: () => invalidateDispatchQueries(queryClient),
  })
}

export function useDispatchTransfer() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (transferId: string) => dispatchAPI.dispatch(transferId),
    onSuccess: () => invalidateDispatchQueries(queryClient),
  })
}

export function useMarkDelivered() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (transferId: string) => dispatchAPI.delivered(transferId),
    onSuccess: () => {
      invalidateDispatchQueries(queryClient)
      queryClient.invalidateQueries({ queryKey: ['emergencies'] })
    },
  })
}