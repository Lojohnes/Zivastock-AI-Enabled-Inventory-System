export interface ModelVersion {
  id: number
  model_name: string
  algorithm: string
  version: string
  dataset_version?: string | null
  feature_set_version?: string | null
  features: string[]
  hyperparameters: Record<string, unknown>
  evaluation_metrics: Record<string, number | string>
  status: string
  created_at: string
}

export interface RecommendationOutcomeSummary {
  total_recommendations: number
  pending: number
  approved: number
  rejected: number
  overridden: number
  completed: number
  outcomes: { success: number; partial: number; failed: number }
  completion_rate: number
  success_rate: number
}

export interface ScenarioResult {
  current_quantity: number
  adjusted_daily_demand: number
  demand_change_pct: number
  supplier_delay_days: number
  safety_stock: number
  days_until_stockout?: number | null
  ending_quantity_after_horizon: number
  stockout_risk: string
}
