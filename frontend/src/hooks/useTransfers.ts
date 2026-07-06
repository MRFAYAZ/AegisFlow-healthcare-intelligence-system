import { useQuery, useQueryClient } from '@tanstack/react-query'
import { redistributionAPI } from '../services/api'
import type { Transfer } from '../types/transfer'
import { useAppStore } from '../store/useAppStore'

export function useTransfers() {
  const queryClient = useQueryClient()

  const updateTransferStatus = (id: string, status: Transfer['status'], eta: string) => {
    const current = queryClient.getQueryData<Transfer[]>(['transfers']) ?? []
    const next = current.map((transfer) => transfer.id === id ? { ...transfer, status, eta } : transfer)
    queryClient.setQueryData(['transfers'], next)
    useAppStore.getState().updateTransferStatus(id, status, eta)
  }

  const addTransfer = (transfer: Transfer) => {
    const current = queryClient.getQueryData<Transfer[]>(['transfers']) ?? []
    queryClient.setQueryData(['transfers'], [transfer, ...current])
    useAppStore.getState().addTransfer(transfer)
  }

  const query = useQuery<Transfer[]>({
    queryKey: ['transfers'],
    queryFn: async () => {
      const response = await redistributionAPI.getAll()
      return response.data as Transfer[]
    },
  })

  return {
    ...query,
    updateTransferStatus,
    addTransfer,
  }
}