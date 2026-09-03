export type GoalStatus = 'active' | 'completed' | 'abandoned'
export type SessionStatus = 'planned' | 'completed' | 'skipped'

export interface StudyGoal {
  id: string
  subject_id: string | null
  title: string
  description: string | null
  target_date: string | null
  status: GoalStatus
  created_at: string
  updated_at: string
}

export interface StudySession {
  id: string
  subject_id: string | null
  goal_id: string | null
  title: string
  scheduled_date: string
  start_time: string | null
  duration_minutes: number
  status: SessionStatus
  notes: string | null
  created_at: string
  updated_at: string
}

export interface Deadline {
  id: string
  subject_id: string | null
  title: string
  due_date: string
  is_completed: boolean
  notes: string | null
  created_at: string
  updated_at: string
}

export interface CalendarEntry {
  entry_type: 'session' | 'deadline'
  id: string
  title: string
  date: string
  subject_id: string | null
  status: string | null
  start_time: string | null
  duration_minutes: number | null
  is_completed: boolean | null
}

export interface PlannerRecommendation {
  subject: string
  action: string
  reason: string
}

export interface PlannerRecommendationResponse {
  recommendations: PlannerRecommendation[]
}

export interface StudyGoalCreateRequest {
  title: string
  subject_id?: string | null
  description?: string | null
  target_date?: string | null
}

export interface StudyGoalUpdateRequest {
  title?: string
  subject_id?: string | null
  description?: string | null
  target_date?: string | null
  status?: GoalStatus
}

export interface StudySessionCreateRequest {
  title: string
  subject_id?: string | null
  goal_id?: string | null
  scheduled_date: string
  start_time?: string | null
  duration_minutes: number
  notes?: string | null
}

export interface StudySessionUpdateRequest {
  title?: string
  subject_id?: string | null
  goal_id?: string | null
  scheduled_date?: string
  start_time?: string | null
  duration_minutes?: number
  status?: SessionStatus
  notes?: string | null
}

export interface DeadlineCreateRequest {
  title: string
  subject_id?: string | null
  due_date: string
  notes?: string | null
}

export interface DeadlineUpdateRequest {
  title?: string
  subject_id?: string | null
  due_date?: string
  is_completed?: boolean
  notes?: string | null
}

export interface ListSessionsParams {
  start?: string
  end?: string
  subject_id?: string
  status?: SessionStatus
}

export interface ListDeadlinesParams {
  start?: string
  end?: string
  include_completed?: boolean
}

export interface ListGoalsParams {
  status?: GoalStatus
}