import { create } from 'zustand'
import type { Emergency, Transfer, Medicine, User } from '../types'
import { mockEmergencies, mockInventory, mockTransfers } from '../lib/mockData'

interface AppStore {
  user: User | null
  emergencies: Emergency[]
  inventory: Medicine[]
  transfers: Transfer[]
  setUser: (u: User | null) => void
  updateEmergencyStatus: (id: string, status: Emergency['status']) => void
  updateTransferStatus: (id: string, status: Transfer['status'], eta?: string) => void
  addInventoryItem: (item: Medicine) => void
  addTransfer: (t: Transfer) => void
}

export const useAppStore = create<AppStore>((set) => ({
  user: null,
  emergencies: mockEmergencies,
  inventory: mockInventory,
  transfers: mockTransfers,

  setUser: (user) => set({ user }),

  updateEmergencyStatus: (id, status) =>
    set((s) => ({
      emergencies: s.emergencies.map((e) => e.id === id ? { ...e, status } : e),
    })),

  updateTransferStatus: (id, status, eta) =>
    set((s) => ({
      transfers: s.transfers.map((t) => t.id === id ? { ...t, status, ...(eta ? { eta } : {}) } : t),
    })),

  addInventoryItem: (item) =>
    set((s) => ({ inventory: [item, ...s.inventory] })),

  addTransfer: (t) =>
    set((s) => ({ transfers: [t, ...s.transfers] })),
}))
