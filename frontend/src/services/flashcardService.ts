import apiClient from './api'
import type {
  Deck,
  DeckCreateRequest,
  DeckDetail,
  DeckUpdateRequest,
  Flashcard,
  FlashcardCreateRequest,
  FlashcardGenerateRequest,
  FlashcardReviewRequest,
  FlashcardUpdateRequest,
} from '../types/flashcard'

export async function listDecks(): Promise<Deck[]> {
  const response = await apiClient.get<Deck[]>('/decks')
  return response.data
}

export async function createDeck(data: DeckCreateRequest): Promise<Deck> {
  const response = await apiClient.post<Deck>('/decks', data)
  return response.data
}

export async function getDeck(deckId: string): Promise<DeckDetail> {
  const response = await apiClient.get<DeckDetail>(`/decks/${deckId}`)
  return response.data
}

export async function updateDeck(deckId: string, data: DeckUpdateRequest): Promise<Deck> {
  const response = await apiClient.put<Deck>(`/decks/${deckId}`, data)
  return response.data
}

export async function deleteDeck(deckId: string): Promise<void> {
  await apiClient.delete(`/decks/${deckId}`)
}

export async function addFlashcard(deckId: string, data: FlashcardCreateRequest): Promise<Flashcard> {
  const response = await apiClient.post<Flashcard>(`/decks/${deckId}/flashcards`, data)
  return response.data
}

export async function generateFlashcards(
  deckId: string,
  data: FlashcardGenerateRequest = {},
): Promise<Flashcard[]> {
  const response = await apiClient.post<Flashcard[]>(`/decks/${deckId}/flashcards/generate`, data)
  return response.data
}

export async function updateFlashcard(
  deckId: string,
  flashcardId: string,
  data: FlashcardUpdateRequest,
): Promise<Flashcard> {
  const response = await apiClient.put<Flashcard>(`/decks/${deckId}/flashcards/${flashcardId}`, data)
  return response.data
}

export async function deleteFlashcard(deckId: string, flashcardId: string): Promise<void> {
  await apiClient.delete(`/decks/${deckId}/flashcards/${flashcardId}`)
}

export async function getReviewQueue(deckId: string): Promise<Flashcard[]> {
  const response = await apiClient.get<Flashcard[]>(`/decks/${deckId}/review-queue`)
  return response.data
}

export async function reviewFlashcard(
  deckId: string,
  flashcardId: string,
  data: FlashcardReviewRequest,
): Promise<Flashcard> {
  const response = await apiClient.post<Flashcard>(`/decks/${deckId}/flashcards/${flashcardId}/review`, data)
  return response.data
}