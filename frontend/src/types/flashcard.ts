export type MasteryStatus = 'new' | 'learning' | 'mastered'
export type ReviewResult = 'again' | 'good'

export interface FlashcardProgress {
  status: MasteryStatus
  times_reviewed: number
  times_correct: number
  correct_streak: number
  last_reviewed_at: string | null
}

export interface Flashcard {
  id: string
  deck_id: string
  front: string
  back: string
  created_at: string
  updated_at: string
  progress: FlashcardProgress
}

export interface Deck {
  id: string
  subject_id: string | null
  title: string
  description: string | null
  card_count: number
  mastered_count: number
  mastery_percentage: number
  created_at: string
  updated_at: string
}

export interface DeckDetail extends Deck {
  flashcards: Flashcard[]
}

export interface DeckCreateRequest {
  title: string
  subject_id?: string | null
  description?: string | null
}

export interface DeckUpdateRequest {
  title?: string
  subject_id?: string | null
  description?: string | null
}

export interface FlashcardCreateRequest {
  front: string
  back: string
}

export interface FlashcardUpdateRequest {
  front?: string
  back?: string
}

export interface FlashcardGenerateRequest {
  count?: number
}

export interface FlashcardReviewRequest {
  result: ReviewResult
}