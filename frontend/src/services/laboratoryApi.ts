import api from './api'
import { ModelVersion, RecommendationOutcomeSummary, ScenarioResult } from '../types/laboratory'

export const fetchModelVersions = async (): Promise<ModelVersion[]> => {
  const response = await api.get<ModelVersion[]>('/anomalies/models')
  return response.data
}

export const fetchRecommendationOutcomeSummary = async (): Promise<RecommendationOutcomeSummary> => {
  const response = await api.get<RecommendationOutcomeSummary>('/recommendations/outcomes/summary')
  return response.data
}

export const runScenario = async (payload: {
  current_quantity: number
  predicted_daily_demand: number
  safety_stock: number
  horizon_days: number
  demand_change_pct: number
  supplier_delay_days: number
}): Promise<ScenarioResult> => {
  const response = await api.post<ScenarioResult>('/forecast/scenario', payload)
  return response.data
}
