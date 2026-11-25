import { useQuery } from '@tanstack/react-query'
import { inventoryAPI } from '../services/api'
import type { InventoryRecord } from '../types/inventory'

export function useInventory() {
  return useQuery<InventoryRecord[]>({
    queryKey: ['inventory'],

    queryFn: async () => {
      const response =
        await inventoryAPI.getAll()

      return response.data
    }
  })
}