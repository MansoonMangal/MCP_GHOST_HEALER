import axios from 'axios'

const api = axios.create({ baseURL: '/api', timeout: 10_000 })

export interface HealingRecord {
  healing_id: string
  test_name: string | null
  original_locator: string
  healed_locator: string | null
  confidence_score: number
  confidence_level: 'LOW' | 'MEDIUM' | 'HIGH'
  decision: 'AUTO_HEAL' | 'MANUAL_REVIEW' | 'FAIL'
  failure_reason: string
  page_url: string
  timestamp: string
  was_successful: boolean
  score_breakdown: Record<string, number> | null
}

export interface ConfidenceReport {
  total_healed: number
  auto_heal_count: number
  manual_review_count: number
  fail_count: number
  avg_confidence_score: number
  high_confidence_count: number
  medium_confidence_count: number
  low_confidence_count: number
  success_rate_percent: number
  score_distribution: { range: string; count: number }[]
  most_unstable_locators: { locator: string; failure_count: number }[]
}

export const fetchHealingHistory = (limit = 50): Promise<HealingRecord[]> =>
  api.get('/healing-history', { params: { limit } }).then(r => r.data)

export const fetchConfidenceReport = (): Promise<ConfidenceReport> =>
  api.get('/confidence-report').then(r => r.data)

export const fetchExecutionTrace = (healingId: string) =>
  api.get(`/execution-trace/${healingId}`).then(r => r.data)
