export interface AuditLogEntry {
  id: string
  actor_id: string | null
  actor_email: string
  target_user_id: string | null
  target_email: string | null
  action: string
  details: string | null
  created_at: string
}

export interface AuditLogListResponse {
  items: AuditLogEntry[]
  total: number
  page: number
  page_size: number
  total_pages: number
}