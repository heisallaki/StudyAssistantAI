import apiClient from './api'
import type {
  Conversation,
  ConversationCreateRequest,
  ConversationDetail,
  ConversationUpdateRequest,
  Message,
} from '../types/tutor'

export async function listConversations(): Promise<Conversation[]> {
  const response = await apiClient.get<Conversation[]>('/tutor/conversations')
  return response.data
}

export async function createConversation(data: ConversationCreateRequest): Promise<Conversation> {
  const response = await apiClient.post<Conversation>('/tutor/conversations', data)
  return response.data
}

export async function getConversation(conversationId: string): Promise<ConversationDetail> {
  const response = await apiClient.get<ConversationDetail>(`/tutor/conversations/${conversationId}`)
  return response.data
}

export async function updateConversation(
  conversationId: string,
  data: ConversationUpdateRequest,
): Promise<Conversation> {
  const response = await apiClient.put<Conversation>(`/tutor/conversations/${conversationId}`, data)
  return response.data
}

export async function deleteConversation(conversationId: string): Promise<void> {
  await apiClient.delete(`/tutor/conversations/${conversationId}`)
}

export async function sendMessage(conversationId: string, content: string): Promise<Message> {
  const response = await apiClient.post<Message>(`/tutor/conversations/${conversationId}/messages`, { content })
  return response.data
}