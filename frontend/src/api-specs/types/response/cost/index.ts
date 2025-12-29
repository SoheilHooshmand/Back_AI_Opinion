export interface TokenCostSimulationDetails {
  num_silicon_people: number
  num_questions: number
  total_requests: number
}

export interface TokenCostTokens {
  input: number
  output: number
}

export interface TokenCostUsd {
  input: number
  output: number
  total: number
}

export interface TokenCostData {
  model: string
  simulation_details: TokenCostSimulationDetails
  tokens: TokenCostTokens
  cost_usd: TokenCostUsd
}

export interface TokenCostResponse {
  success: boolean
  message: string
  data: TokenCostData
  status_code: number
  code: string
}
