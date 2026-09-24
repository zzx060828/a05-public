export const AVATAR_METRICS_ENABLED_KEY = 'avatar_connect_metrics_enabled'
export const AVATAR_METRICS_STORAGE_KEY = 'avatar_connect_metrics_v1'

export type AvatarConnectMetric = {
  runId: string
  finishedAt: string
  outcome: 'success' | 'failure' | 'aborted'
  attempts: number
  firstSuccess: boolean
  finalSuccess: boolean
  durationMs: number
  errorName: string
}

export function avatarMetricsEnabled(): boolean {
  try {
    return localStorage.getItem(AVATAR_METRICS_ENABLED_KEY) === '1'
  } catch {
    return false
  }
}

export function recordAvatarConnectMetric(metric: AvatarConnectMetric): void {
  try {
    const stored = JSON.parse(localStorage.getItem(AVATAR_METRICS_STORAGE_KEY) || '[]')
    const rows: AvatarConnectMetric[] = Array.isArray(stored) ? stored : []
    localStorage.setItem(AVATAR_METRICS_STORAGE_KEY, JSON.stringify([...rows.slice(-499), metric]))
    console.info('[avatar-connect-metric]', metric)
  } catch (error) {
    console.warn('[avatar-connect-metric] 无法保存测试记录', error)
  }
}
