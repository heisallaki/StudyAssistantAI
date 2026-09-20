import apiClient from './api'
import type { AuthUser, LoginRequest, RegisterRequest, TokenResponse } from '../types/auth'

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