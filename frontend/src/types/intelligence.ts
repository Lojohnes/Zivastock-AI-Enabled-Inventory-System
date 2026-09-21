export interface IntelligenceSummary {
  total_products: number
  critical_risks: number
  high_risks: number
  stockout_risks: number
  excess_inventory: number
  pending_recommendations: number
  data_quality_score?: number | null
}

export interface RiskRecord {
  id: number
  product_id: number
  product_name?: string | null
  location_id?: number | null
  calculation_date: string
  total_score: number
  risk_level: string
  abc_class?: string | null
  priority: string
  anomaly_score: number
  variance_score: number
  financial_value_score: number
  stockout_score: number
  adjustment_score: number
  accuracy_score: number
  explanation: string[]
}

export interface ExposureRecord {
  id: number
  product_id: number
  product_name?: string | null
  calculation_date: string
  current_quantity: number
  predicted_daily_demand: number
  safety_stock: number
  days_until_stockout?: number | null
  stockout_date?: string | null
  stockout_risk: string
  excess_quantity: number
  slow_moving: boolean
  non_moving: boolean
  explanation: string[]
}

export interface RecommendationRecord {
  id: number
  product_id: number
  product_name?: string | null
  recommendation_type: string
  recommendation_text: string
  priority: string
  confidence_score?: number | null
  evidence: string[]
  expected_impact: Record<string, unknown>
  status: string
}

export interface CommandCentreResponse {
  summary: IntelligenceSummary
  top_risks: RiskRecord[]
  stockout_exposures: ExposureRecord[]
  recommendations: RecommendationRecord[]
}

export interface ProductIntelligence {
  product: { id: number; barcode: string; description: string; unit_cost: number }
  risk_scores: RiskRecord[]
  exposures: ExposureRecord[]
  recommendations: RecommendationRecord[]
}
