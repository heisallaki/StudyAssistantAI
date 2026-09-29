import apiClient from './api'
import type { AuthUser, LoginRequest, RegisterRequest, TokenResponse } from '../types/auth'
import type {
  AccountDeletionRequest,
  EmailVerificationRequest,
  MessageResponse,
  OtpRequestByEmail,
  PasswordChangeRequest,
} from '../types/otp'

export async function login(credentials: LoginRequest): Promise<TokenResponse> {
  const response = await apiClient.post<TokenResponse>('/auth/login', credentials)
  return response.data
}

export async function register(credentials: RegisterRequest): Promise<AuthUser> {
  const response = await apiClient.post<AuthUser>('/auth/register', credentials)
  return response.data
}

export async function getCurrentUser(): Promise<AuthUser> {
  const response = await apiClient.get<AuthUser>('/auth/me')
  return response.data
}

export async function verifyEmail(data: EmailVerificationRequest): Promise<AuthUser> {
  const response = await apiClient.post<AuthUser>('/auth/verify-email', data)
  return response.data
}

export async function resendVerification(data: OtpRequestByEmail): Promise<MessageResponse> {
  const response = await apiClient.post<MessageResponse>('/auth/resend-verification', data)
  return response.data
}

export async function requestPasswordChangeOtp(): Promise<MessageResponse> {
  const response = await apiClient.post<MessageResponse>('/auth/request-password-change-otp')
  return response.data
}

export async function changePassword(data: PasswordChangeRequest): Promise<MessageResponse> {
  const response = await apiClient.post<MessageResponse>('/auth/change-password', data)
  return response.data
}

export async function requestAccountDeletionOtp(): Promise<MessageResponse> {
  const response = await apiClient.post<MessageResponse>('/auth/request-account-deletion-otp')
  return response.data
}

export async function deleteOwnAccount(data: AccountDeletionRequest): Promise<void> {
  await apiClient.delete('/auth/me', { data })
}