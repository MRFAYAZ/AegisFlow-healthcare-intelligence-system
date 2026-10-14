import { useQuery } from '@tanstack/react-query'
import { inventoryAPI } from '../services/api'
import type { ShortageRiskAssessment } from '../types'

export function useShortagePredictions() {
	return useQuery<ShortageRiskAssessment[]>({
		queryKey: ['shortage-predictions'],
		queryFn: async () => (await inventoryAPI.getShortagePredictions()).data,
		staleTime: 30000,
	})
}
