import apiClient from './api'
import type {
  Subject,
  SubjectCreateRequest,
  SubjectDetail,
  SubjectUpdateRequest,
  Topic,
  TopicCreateRequest,
  TopicUpdateRequest,
} from '../types/subject'

export async function listSubjects(): Promise<Subject[]> {
  const response = await apiClient.get<Subject[]>('/subjects')
  return response.data
}

export async function createSubject(data: SubjectCreateRequest): Promise<Subject> {
  const response = await apiClient.post<Subject>('/subjects', data)
  return response.data
}

export async function getSubject(subjectId: string): Promise<SubjectDetail> {
  const response = await apiClient.get<SubjectDetail>(`/subjects/${subjectId}`)
  return response.data
}

export async function updateSubject(subjectId: string, data: SubjectUpdateRequest): Promise<Subject> {
  const response = await apiClient.put<Subject>(`/subjects/${subjectId}`, data)
  return response.data
}

export async function deleteSubject(subjectId: string): Promise<void> {
  await apiClient.delete(`/subjects/${subjectId}`)
}

export async function createTopic(subjectId: string, data: TopicCreateRequest): Promise<Topic> {
  const response = await apiClient.post<Topic>(`/subjects/${subjectId}/topics`, data)
  return response.data
}

export async function updateTopic(subjectId: string, topicId: string, data: TopicUpdateRequest): Promise<Topic> {
  const response = await apiClient.put<Topic>(`/subjects/${subjectId}/topics/${topicId}`, data)
  return response.data
}

export async function deleteTopic(subjectId: string, topicId: string): Promise<void> {
  await apiClient.delete(`/subjects/${subjectId}/topics/${topicId}`)
}