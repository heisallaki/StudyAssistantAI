import apiClient from './api'
import type { AuditLogListResponse } from '../types/auditLog'

export async function listAuditLog(page: number, pageSize: number): Promise<AuditLogListResponse> {
  const response = await apiClient.get<AuditLogListResponse>('/admin/audit-log', {
    params: { page, page_size: pageSize },
  })
  return response.data
}