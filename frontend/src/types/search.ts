export type SearchResultType = 'subject' | 'topic' | 'document' | 'quiz' | 'flashcard_deck'

export interface SearchResult {
  result_type: SearchResultType
  id: string
  title: string
  snippet: string | null
  subject_id: string | null
}

export interface SearchResponse {
  query: string
  results: SearchResult[]
}

export interface SemanticSearchRequest {
  query: string
  subject_id?: string | null
}

export interface SemanticSearchResult {
  document_id: string
  document_title: string
  subject_id: string | null
  chunk_text: string
  similarity_percentage: number
}

export interface SemanticSearchResponse {
  query: string
  results: SemanticSearchResult[]
}