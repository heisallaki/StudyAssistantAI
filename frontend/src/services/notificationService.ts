import apiClient from './api'
import type { Notification, UnreadCount } from '../types/notification'

export async function listNotifications(unreadOnly = false): Promise<Notification[]> {
  const response = await apiClient.get<Notification[]>('/notifications', {
    params: { unread_only: unreadOnly },
  })
  return response.data
}

export async function getUnreadCount(): Promise<UnreadCount> {
  const response = await apiClient.get<UnreadCount>('/notifications/unread-count')
  return response.data
}

export async function setRead(notificationId: string, isRead: boolean): Promise<Notification> {
  const response = await apiClient.put<Notification>(`/notifications/${notificationId}`, { is_read: isRead })
  return response.data
}

export async function markAllRead(): Promise<UnreadCount> {
  const response = await apiClient.post<UnreadCount>('/notifications/mark-all-read')
  return response.data
}

export async function deleteNotification(notificationId: string): Promise<void> {
  await apiClient.delete(`/notifications/${notificationId}`)
}