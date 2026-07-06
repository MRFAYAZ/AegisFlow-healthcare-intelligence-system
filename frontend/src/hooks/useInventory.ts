import { useQuery } from '@tanstack/react-query'
import { inventoryAPI } from '../services/api'
import type { Medicine } from '../types'

export function useInventory() {
  return useQuery<Medicine[]>({
    queryKey: ['inventory'],

    queryFn: async () => {
      const response =
        await inventoryAPI.getAll()

      return response.data
    }
  })
}