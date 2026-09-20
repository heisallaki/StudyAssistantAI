export type Difficulty = 'easy' | 'medium' | 'hard'
export type QuestionType = 'multiple_choice' | 'true_false' | 'short_answer'
export type GenerationStatus = 'pending' | 'completed' | 'failed'

export interface QuizQuestion {
  id: string
  order_index: number
  question_type: QuestionType
  prompt: string
  options: string[]
  correct_answer: string
  explanation: string
}

export interface Quiz {
  id: string
  subject_id: string | null
  title: string
  difficulty: Difficulty
  generation_status: GenerationStatus
  generation_error: string | null
  question_count: number
  created_at: string
  updated_at: string
}

export interface QuizDetail extends Quiz {
  questions: QuizQuestion[]
}

export interface QuizCreateRequest {
  subject_id?: string | null
  difficulty?: Difficulty
  question_types?: QuestionType[]
  question_count?: number
}