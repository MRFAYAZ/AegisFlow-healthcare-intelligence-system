import { useQuery } from '@tanstack/react-query'
import { analyticsAPI } from '../services/api'

export function useDashboard() {

  return useQuery({
    queryKey: ['dashboard'],

    queryFn: async () => {

      const response = await analyticsAPI.getDashboard()

      console.log("Dashboard API Response")
      console.log(response)

      console.log("Dashboard Data")
      console.log(response.data)

      return response.data
    }
  })
}