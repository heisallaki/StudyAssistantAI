import apiClient from './api'
import type {
  AnalyticsOverview,
  PerformanceTrendPoint,
  StudyTimePoint,
  SubjectBreakdown,
  WeakArea,
} from '../types/analytics'

export async function getOverview(): Promise<AnalyticsOverview> {
  const response = await apiClient.get<AnalyticsOverview>('/analytics/overview')
  return response.data
}

export async function getPerformanceTrend(days = 30): Promise<PerformanceTrendPoint[]> {
  const response = await apiClient.get<PerformanceTrendPoint[]>('/analytics/performance-trend', {
    params: { days },
  })
  return response.data
}

export async function getStudyTime(days = 30): Promise<StudyTimePoint[]> {
  const response = await apiClient.get<StudyTimePoint[]>('/analytics/study-time', { params: { days } })
  return response.data
}

export async function getSubjectBreakdown(): Promise<SubjectBreakdown[]> {
  const response = await apiClient.get<SubjectBreakdown[]>('/analytics/subject-breakdown')
  return response.data
}

export async function getWeakAreas(): Promise<WeakArea[]> {
  const response = await apiClient.get<WeakArea[]>('/analytics/weak-areas')
  return response.data
}