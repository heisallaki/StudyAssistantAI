export type ProcessingStatus = 'pending' | 'processed' | 'failed'
export type IndexingStatus = 'pending' | 'indexed' | 'failed' | 'not_applicable'

export interface Document {
  id: string
  subject_id: string | null
  original_filename: string
  content_type: string
  file_size_bytes: number
  processing_status: ProcessingStatus
  processing_error: string | null
  indexing_status: IndexingStatus
  indexing_error: string | null
  created_at: string
  updated_at: string
}

export interface DocumentDetail extends Document {
  extracted_text: string | null
}

export interface DocumentUpdateRequest {
  subject_id?: string | null
}