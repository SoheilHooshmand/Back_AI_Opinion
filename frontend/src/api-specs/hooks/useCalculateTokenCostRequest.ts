// hooks/useTokenCost.ts
import { useMutation } from '@tanstack/react-query'
import { calculateTokenCostRequest } from '../api'
import type { TokenCostResponse } from '../types/response/cost'

export function useCalculateTokenCostRequest() {
  return useMutation<TokenCostResponse, Error, FormData>({
    mutationFn: (data: FormData) => calculateTokenCostRequest(data).then((res) => res.data),
  })
}
