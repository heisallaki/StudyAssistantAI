export interface AnalyticsOverview {
  total_study_minutes: number
  total_quizzes_taken: number
  average_quiz_score: number | null
  total_flashcards_reviewed: number
  flashcards_mastered: number
  total_flashcards: number
  subjects_count: number
  active_goals_count: number
}

export interface PerformanceTrendPoint {
  date: string
  average_score: number
  attempts_count: number
}

export interface StudyTimePoint {
  date: string
  minutes: number
}

export interface SubjectBreakdown {
  subject_id: string
  name: string
  priority: string
  topic_progress_percentage: number
  quiz_average_score: number | null
  flashcard_mastery_percentage: number | null
  study_minutes: number
}

export interface WeakArea {
  subject_id: string
  name: string
  reason: string
  metric_value: number
}