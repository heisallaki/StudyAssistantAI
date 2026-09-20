import apiClient from './api'
import type { Quiz, QuizCreateRequest, QuizDetail } from '../types/quiz'

export async function listQuizzes(): Promise<Quiz[]> {
  const response = await apiClient.get<Quiz[]>('/quizzes')
  return response.data
}

export async function createQuiz(data: QuizCreateRequest): Promise<QuizDetail> {
  const response = await apiClient.post<QuizDetail>('/quizzes', data)
  return response.data
}

export async function getQuiz(quizId: string): Promise<QuizDetail> {
  const response = await apiClient.get<QuizDetail>(`/quizzes/${quizId}`)
  return response.data
}

export async function deleteQuiz(quizId: string): Promise<void> {
  await apiClient.delete(`/quizzes/${quizId}`)
}