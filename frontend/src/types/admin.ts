export interface AdminUser {
  id: string
  email: string
  is_active: boolean
  is_superuser: boolean
  created_at: string
  updated_at: string
  subject_count: number
  document_count: number
  conversation_count: number
  quiz_count: number
  quiz_attempt_count: number
  flashcard_deck_count: number
}

export interface AdminUserListResponse {
  items: AdminUser[]
  total: number
  page: number
  page_size: number
  total_pages: number
}

export interface AdminUserListParams {
  search?: string
  is_active?: boolean
  is_superuser?: boolean
  page?: number
  page_size?: number
}

export interface AdminUserUpdateRequest {
  is_active?: boolean
  is_superuser?: boolean
}

export interface AdminSystemStats {
  total_users: number
  active_users: number
  inactive_users: number
  admin_users: number
  new_users_last_7_days: number
  new_users_last_30_days: number
  total_subjects: number
  total_topics: number
  total_documents: number
  total_conversations: number
  total_messages: number
  total_quizzes: number
  total_quiz_attempts: number
  total_flashcard_decks: number
  total_flashcards: number
  total_study_goals: number
  total_study_sessions: number
  total_deadlines: number
  total_notifications: number
}