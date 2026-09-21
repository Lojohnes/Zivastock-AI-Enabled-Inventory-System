import api from './api'
import { CommandCentreResponse, ProductIntelligence } from '../types/intelligence'

export const fetchCommandCentre = async (limit = 10): Promise<CommandCentreResponse> => {
  const response = await api.get<CommandCentreResponse>('/risk/command-centre', { params: { limit } })
  return response.data
}

export const fetchProductIntelligence = async (productId: number): Promise<ProductIntelligence> => {
  const response = await api.get<ProductIntelligence>(`/risk/product/${productId}`)
  return response.data
}

export const decideRecommendation = async (
  recommendationId: number,
  decision: 'APPROVED' | 'REJECTED' | 'OVERRIDDEN',
  reason?: string,
) => {
  const response = await api.post(`/recommendations/${recommendationId}/decision`, {
    decision,
    reason,
  })
  return response.data
}
