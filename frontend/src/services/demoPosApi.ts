import api from './api'
import { DemoPosResponse } from '../types/demoPos'

export const generateDemoTransactions = async (scenario: string, days: number, seed: number) => {
  const response = await api.get<DemoPosResponse>('/demo-pos/generate', { params: { scenario, days, seed } })
  return response.data
}

export const runDemoPipeline = async (scenario: string, days: number, seed: number) => {
  const response = await api.post('/demo-pos/run-pipeline', null, { params: { scenario, days, seed } })
  return response.data
}
