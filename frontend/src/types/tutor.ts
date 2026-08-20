export type ConversationMode = 'tutor' | 'socratic'
export type ExplanationLevel = 'beginner' | 'intermediate' | 'advanced'

export interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  sources: string[]
  created_at: string
}

export interface Conversation {
  id: string
  subject_id: string | null
  title: string
  mode: ConversationMode
  explanation_level: ExplanationLevel
  created_at: string
  updated_at: string
}

export interface ConversationDetail extends Conversation {
  messages: Message[]
}

export interface ConversationCreateRequest {
  subject_id?: string | null
  mode?: ConversationMode
  explanation_level?: ExplanationLevel
}

export interface ConversationUpdateRequest {
  title?: string
  mode?: ConversationMode
  explanation_level?: ExplanationLevel
}