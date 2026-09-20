import apiClient from './api'
import type { Profile, ProfileUpdateRequest } from '../types/profile'

export async function getProfile(): Promise<Profile> {
  const response = await apiClient.get<Profile>('/profile/me')
  return response.data
}

export async function updateProfile(updates: ProfileUpdateRequest): Promise<Profile> {
  const response = await apiClient.patch<Profile>('/profile/me', updates)
  return response.data
}