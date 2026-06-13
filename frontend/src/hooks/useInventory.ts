import { useQuery } from '@tanstack/react-query'
import { inventoryAPI } from '../services/api'

export function useInventory() {

  return useQuery({
    queryKey: ['inventory'],

    queryFn: async () => {

      const response =
        await inventoryAPI.getAll()

      return response.data
    }
  })
}