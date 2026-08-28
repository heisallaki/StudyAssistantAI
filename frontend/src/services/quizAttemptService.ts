import apiClient from './api'
import type {
  ListAttemptsParams,
  QuizAttempt,
  QuizAttemptDetail,
  SubmitAnswerRequest,
} from '../types/quizAttempt'

export async function startAttempt(quizId: string): Promise<QuizAttemptDetail> {
  const response = await apiClient.post<QuizAttemptDetail>(`/quizzes/${quizId}/attempts`)
  return response.data
}

export async function getAttempt(attemptId: string): Promise<QuizAttemptDetail> {
  const response = await apiClient.get<QuizAttemptDetail>(`/quiz-attempts/${attemptId}`)
  return response.data
}

export async function submitAnswer(
  attemptId: string,
  questionId: string,
  data: SubmitAnswerRequest,
): Promise<QuizAttemptDetail> {
  const response = await apiClient.put<QuizAttemptDetail>(
    `/quiz-attempts/${attemptId}/answers/${questionId}`,
    data,
  )
  return response.data
}

export async function completeAttempt(attemptId: string): Promise<QuizAttemptDetail> {
  const response = await apiClient.post<QuizAttemptDetail>(`/quiz-attempts/${attemptId}/complete`)
  return response.data
}

export async function listAttempts(params: ListAttemptsParams = {}): Promise<QuizAttempt[]> {
  const response = await apiClient.get<QuizAttempt[]>('/quiz-attempts', { params })
  return response.data
}