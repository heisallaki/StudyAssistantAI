import apiClient from './api'
import type {
  CalendarEntry,
  Deadline,
  DeadlineCreateRequest,
  DeadlineUpdateRequest,
  ListDeadlinesParams,
  ListGoalsParams,
  ListSessionsParams,
  PlannerRecommendationResponse,
  StudyGoal,
  StudyGoalCreateRequest,
  StudyGoalUpdateRequest,
  StudySession,
  StudySessionCreateRequest,
  StudySessionUpdateRequest,
} from '../types/planner'

export async function listGoals(params: ListGoalsParams = {}): Promise<StudyGoal[]> {
  const response = await apiClient.get<StudyGoal[]>('/planner/goals', { params })
  return response.data
}

export async function createGoal(data: StudyGoalCreateRequest): Promise<StudyGoal> {
  const response = await apiClient.post<StudyGoal>('/planner/goals', data)
  return response.data
}

export async function updateGoal(goalId: string, data: StudyGoalUpdateRequest): Promise<StudyGoal> {
  const response = await apiClient.put<StudyGoal>(`/planner/goals/${goalId}`, data)
  return response.data
}

export async function deleteGoal(goalId: string): Promise<void> {
  await apiClient.delete(`/planner/goals/${goalId}`)
}

export async function listSessions(params: ListSessionsParams = {}): Promise<StudySession[]> {
  const response = await apiClient.get<StudySession[]>('/planner/sessions', { params })
  return response.data
}

export async function createSession(data: StudySessionCreateRequest): Promise<StudySession> {
  const response = await apiClient.post<StudySession>('/planner/sessions', data)
  return response.data
}

export async function updateSession(sessionId: string, data: StudySessionUpdateRequest): Promise<StudySession> {
  const response = await apiClient.put<StudySession>(`/planner/sessions/${sessionId}`, data)
  return response.data
}

export async function deleteSession(sessionId: string): Promise<void> {
  await apiClient.delete(`/planner/sessions/${sessionId}`)
}

export async function listDeadlines(params: ListDeadlinesParams = {}): Promise<Deadline[]> {
  const response = await apiClient.get<Deadline[]>('/planner/deadlines', { params })
  return response.data
}

export async function createDeadline(data: DeadlineCreateRequest): Promise<Deadline> {
  const response = await apiClient.post<Deadline>('/planner/deadlines', data)
  return response.data
}

export async function updateDeadline(deadlineId: string, data: DeadlineUpdateRequest): Promise<Deadline> {
  const response = await apiClient.put<Deadline>(`/planner/deadlines/${deadlineId}`, data)
  return response.data
}

export async function deleteDeadline(deadlineId: string): Promise<void> {
  await apiClient.delete(`/planner/deadlines/${deadlineId}`)
}

export async function getCalendar(start: string, end: string): Promise<CalendarEntry[]> {
  const response = await apiClient.get<CalendarEntry[]>('/planner/calendar', { params: { start, end } })
  return response.data
}

export async function getRecommendations(): Promise<PlannerRecommendationResponse> {
  const response = await apiClient.post<PlannerRecommendationResponse>('/planner/recommendations')
  return response.data
}