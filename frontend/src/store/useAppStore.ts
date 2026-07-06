import { create } from 'zustand'
import type { Medicine, User } from '../types'
import type { Transfer } from '../types/transfer'

interface AppState {
  user: User | null
  inventoryItems: Medicine[]
  transfers: Transfer[]
  setUser: (user: User | null) => void
  addInventoryItem: (item: Medicine) => void
  addTransfer: (transfer: Transfer) => void
  updateTransferStatus: (id: string, status: Transfer['status'], eta: string) => void
}

export const useAppStore = create<AppState>((set) => ({
  user: null,
  inventoryItems: [],
  transfers: [],
  setUser: (user) => set({ user }),
  addInventoryItem: (item) => set((state) => ({ inventoryItems: [...state.inventoryItems, item] })),
  addTransfer: (transfer) => set((state) => ({ transfers: [...state.transfers, transfer] })),
  updateTransferStatus: (id, status, eta) => set((state) => ({
    transfers: state.transfers.map((transfer) => transfer.id === id ? { ...transfer, status, eta } : transfer),
  })),
}))
