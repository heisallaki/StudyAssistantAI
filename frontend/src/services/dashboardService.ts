import apiClient from './api'
import type { DashboardOverview } from '../types/dashboard'

export async function getOverview(): Promise<DashboardOverview> {
  const response = await apiClient.get<DashboardOverview>('/dashboard/overview')
  return response.data
}