export interface DemoTransaction {
  source_record_id: string
  barcode: string
  product_code: string
  description: string
  location_name: string
  event_type: string
  quantity: number
  unit_cost: number
  transaction_value: number
  event_timestamp: string
  reference_number: string
}

export interface DemoPosResponse {
  scenario: string
  days: number
  seed: number
  records: number
  transactions: DemoTransaction[]
}
