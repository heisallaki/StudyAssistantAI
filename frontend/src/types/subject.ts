export interface Topic {
  id: string
  subject_id: string
  title: string
  description: string | null
  is_completed: boolean
  order_index: number
  created_at: string
  updated_at: string
}

export interface Subject {
  id: string
  name: string
  description: string | null
  color: string | null
  topic_count: number
  completed_topic_count: number
  progress_percentage: number
  created_at: string
  updated_at: string
}

export interface SubjectDetail extends Subject {
  topics: Topic[]
}

export interface SubjectCreateRequest {
  name: string
  description?: string | null
  color?: string | null
}

export interface SubjectUpdateRequest {
  name?: string
  description?: string | null
  color?: string | null
}

export interface TopicCreateRequest {
  title: string
  description?: string | null
  order_index?: number
}

export interface TopicUpdateRequest {
  title?: string
  description?: string | null
  is_completed?: boolean
  order_index?: number
}