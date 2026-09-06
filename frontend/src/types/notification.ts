export type NotificationType = 'study_reminder' | 'deadline_reminder' | 'quiz_reminder' | 'system'

export interface Notification {
  id: string
  notification_type: NotificationType
  title: string
  message: string
  related_id: string | null
  is_read: boolean
  created_at: string
}

export interface UnreadCount {
  unread_count: number
}