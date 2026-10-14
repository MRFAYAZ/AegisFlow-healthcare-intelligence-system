import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { redistributionAPI, transferAPI } from '../services/api'
import type { Transfer } from '../types/transfer'
import { useAppStore } from '../store/useAppStore'

function normalizeTransfer(item: any): Transfer {
  const status = String(item.transfer_status ?? 'PENDING').toUpperCase()
  return {
    id: String(item.transfer_id),
    medicine: item.medicine_name ?? 'Unknown medicine',
    from: item.from_facility_name ?? 'Unknown source',
    to: item.to_facility_name ?? 'Unknown destination',
    quantity: `${item.approved_quantity ?? item.requested_quantity ?? 0} units`,
    status: status === 'IN_TRANSIT' ? 'in_transit' : status === 'COMPLETED' ? 'delivered' : status === 'APPROVED' ? 'sourcing' : 'pending',
    eta: status === 'IN_TRANSIT' ? 'En route' : '—',
    createdAt: item.requested_at ?? new Date().toISOString(),
  }
}

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
      return (response.data ?? []).map(normalizeTransfer)
    },
  })

  const approveMutation = useMutation({
    mutationFn: ({ id, quantity }: { id: string; quantity: number }) => transferAPI.approve(id, quantity),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['transfers'] }),
  })

  return {
    ...query,
    updateTransferStatus,
    addTransfer,
    approveTransfer: (id: string, quantity: number) => approveMutation.mutateAsync({ id, quantity }),
    isApproving: approveMutation.isPending,
  }
}