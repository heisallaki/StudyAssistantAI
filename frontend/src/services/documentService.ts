import apiClient from './api'
import type { Document, DocumentDetail, DocumentUpdateRequest } from '../types/document'

export async function listDocuments(subjectId?: string): Promise<Document[]> {
  const response = await apiClient.get<Document[]>('/documents', {
    params: subjectId ? { subject_id: subjectId } : undefined,
  })
  return response.data
}

export async function uploadDocument(file: File, subjectId?: string): Promise<DocumentDetail> {
  const formData = new FormData()
  formData.append('file', file)
  if (subjectId) {
    formData.append('subject_id', subjectId)
  }
  const response = await apiClient.post<DocumentDetail>('/documents', formData, {
    headers: { 'Content-Type': undefined },
  })
  return response.data
}

export async function getDocument(documentId: string): Promise<DocumentDetail> {
  const response = await apiClient.get<DocumentDetail>(`/documents/${documentId}`)
  return response.data
}

export async function updateDocument(documentId: string, data: DocumentUpdateRequest): Promise<Document> {
  const response = await apiClient.put<Document>(`/documents/${documentId}`, data)
  return response.data
}

export async function deleteDocument(documentId: string): Promise<void> {
  await apiClient.delete(`/documents/${documentId}`)
}

export async function reindexDocument(documentId: string): Promise<DocumentDetail> {
  const response = await apiClient.post<DocumentDetail>(`/documents/${documentId}/reindex`)
  return response.data
}

export async function downloadDocument(documentId: string, filename: string): Promise<void> {
  const response = await apiClient.get(`/documents/${documentId}/download`, {
    responseType: 'blob',
  })
  const blobUrl = URL.createObjectURL(response.data as Blob)
  const link = document.createElement('a')
  link.href = blobUrl
  link.download = filename
  document.body.appendChild(link)
  link.click()
  link.remove()
  URL.revokeObjectURL(blobUrl)
}