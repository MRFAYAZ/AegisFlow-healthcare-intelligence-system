import { create } from 'zustand'
import type { Medicine, User } from '../types'
import type { Transfer } from '../types/transfer'

export type ThemePreference = 'system' | 'light' | 'dark'

const getStoredTheme = (): ThemePreference => {
  if (typeof window === 'undefined') return 'system'
  const stored = window.localStorage.getItem('aegisflow_theme')
  return stored === 'light' || stored === 'dark' ? stored : 'system'
}

const getStoredUser = (): User | null => {
  if (typeof window === 'undefined') return null

  const raw = window.localStorage.getItem('aegisflow_user')
  if (!raw) return null

  try {
    return JSON.parse(raw) as User
  } catch {
    return null
  }
}

interface AppState {
  user: User | null
  theme: ThemePreference
  inventoryItems: Medicine[]
  transfers: Transfer[]
  setUser: (user: User | null) => void
  setTheme: (theme: ThemePreference) => void
  addInventoryItem: (item: Medicine) => void
  addTransfer: (transfer: Transfer) => void
  updateTransferStatus: (id: string, status: Transfer['status'], eta: string) => void
}

export const useAppStore = create<AppState>((set) => ({
  user: getStoredUser(),
  theme: getStoredTheme(),
  inventoryItems: [],
  transfers: [],
  setUser: (user) => {
    if (typeof window !== 'undefined') {
      if (user) {
        window.localStorage.setItem('aegisflow_user', JSON.stringify(user))
      } else {
        window.localStorage.removeItem('aegisflow_user')
      }
    }

    set({ user })
  },
  setTheme: (theme) => {
    if (typeof window !== 'undefined') window.localStorage.setItem('aegisflow_theme', theme)
    set({ theme })
  },
  addInventoryItem: (item) => set((state) => ({ inventoryItems: [...state.inventoryItems, item] })),
  addTransfer: (transfer) => set((state) => ({ transfers: [...state.transfers, transfer] })),
  updateTransferStatus: (id, status, eta) => set((state) => ({
    transfers: state.transfers.map((transfer) => transfer.id === id ? { ...transfer, status, eta } : transfer),
  })),
}))
