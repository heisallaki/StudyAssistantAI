import apiClient from './api'
import type { SearchResponse, SemanticSearchRequest, SemanticSearchResponse } from '../types/search'

export async function search(query: string): Promise<SearchResponse> {
  const response = await apiClient.get<SearchResponse>('/search', { params: { q: query } })
  return response.data
}

export async function semanticSearch(data: SemanticSearchRequest): Promise<SemanticSearchResponse> {
  const response = await apiClient.post<SemanticSearchResponse>('/search/semantic', data)
  return response.data
}