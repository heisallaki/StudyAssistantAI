import type { QuestionType } from './quiz'

export type AttemptStatus = 'in_progress' | 'completed'

export interface QuizAttempt {
  id: string
  quiz_id: string
  quiz_title: string
  subject_id: string | null
  status: AttemptStatus
  score: number | null
  total_questions: number
  percentage_score: number | null
  started_at: string
  completed_at: string | null
}

export interface QuizAttemptQuestionResult {
  question_id: string
  order_index: number
  question_type: QuestionType
  prompt: string
  options: string[]
  submitted_answer: string | null
  is_correct: boolean | null
  correct_answer: string | null
  explanation: string | null
}

export interface QuizAttemptDetail extends QuizAttempt {
  answers: QuizAttemptQuestionResult[]
}

export interface SubmitAnswerRequest {
  submitted_answer: string
}

export interface ListAttemptsParams {
  quiz_id?: string
  subject_id?: string
}