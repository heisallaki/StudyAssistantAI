import apiClient from './api'
import type {
  AdminSystemStats,
  AdminUser,
  AdminUserListParams,
  AdminUserListResponse,
  AdminUserUpdateRequest,
} from '../types/admin'

export async function listUsers(params: AdminUserListParams): Promise<AdminUserListResponse> {
  const response = await apiClient.get<AdminUserListResponse>('/admin/users', { params })
  return response.data
}

export async function getUser(userId: string): Promise<AdminUser> {
  const response = await apiClient.get<AdminUser>(`/admin/users/${userId}`)
  return response.data
}

export async function updateUser(userId: string, data: AdminUserUpdateRequest): Promise<AdminUser> {
  const response = await apiClient.patch<AdminUser>(`/admin/users/${userId}`, data)
  return response.data
}

export async function deleteUser(userId: string): Promise<void> {
  await apiClient.delete(`/admin/users/${userId}`)
}

export async function getSystemStats(): Promise<AdminSystemStats> {
  const response = await apiClient.get<AdminSystemStats>('/admin/stats')
  return response.data
}