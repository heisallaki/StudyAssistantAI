import { useEffect, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  Chip,
  CircularProgress,
  Container,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  Typography,
} from '@mui/material'
import * as documentService from '../../services/documentService'
import type { DocumentDetail as DocumentDetailType } from '../../types/document'

const STATUS_COLOR: Record<string, 'success' | 'warning' | 'default'> = {
  processed: 'success',
  failed: 'warning',
  pending: 'default',
  indexed: 'success',
  not_applicable: 'default',
}

function formatFileSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}

function DocumentDetailPage() {
  const { documentId } = useParams<{ documentId: string }>()
  const navigate = useNavigate()

  const [documentData, setDocumentData] = useState<DocumentDetailType | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false)
  const [isDeleting, setIsDeleting] = useState(false)
  const [isReindexing, setIsReindexing] = useState(false)
  const [reindexError, setReindexError] = useState<string | null>(null)

  useEffect(() => {
    if (!documentId) return
    documentService
      .getDocument(documentId)
      .then((data) => setDocumentData(data))
      .catch(() => setError('Unable to load this document.'))
      .finally(() => setIsLoading(false))
  }, [documentId])

  async function handleDownload() {
    if (!documentData) return
    await documentService.downloadDocument(documentData.id, documentData.original_filename)
  }

  async function handleReindex() {
    if (!documentId) return
    setReindexError(null)
    setIsReindexing(true)
    try {
      const updated = await documentService.reindexDocument(documentId)
      setDocumentData(updated)
    } catch {
      setReindexError('Unable to index this document right now. Make sure Ollama is running.')
    } finally {
      setIsReindexing(false)
    }
  }

  async function handleDelete() {
    if (!documentId) return
    setIsDeleting(true)
    try {
      await documentService.deleteDocument(documentId)
      navigate('/documents')
    } finally {
      setIsDeleting(false)
    }
  }

  if (isLoading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '60vh' }}>
        <CircularProgress />
      </Box>
    )
  }

  if (error || !documentData) {
    return (
      <Container maxWidth="sm">
        <Alert severity="error" sx={{ mt: 4 }}>
          {error ?? 'Document not found.'}
        </Alert>
      </Container>
    )
  }

  return (
    <Container maxWidth="md">
      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3, py: 4 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: 2, flexWrap: 'wrap' }}>
          <Box>
            <Typography variant="h4" component="h1" sx={{ fontWeight: 600 }}>
              {documentData.original_filename}
            </Typography>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mt: 1, flexWrap: 'wrap' }}>
              <Chip
                label={documentData.processing_status}
                color={STATUS_COLOR[documentData.processing_status] ?? 'default'}
                size="small"
              />
              {documentData.indexing_status !== 'not_applicable' && (
                <Chip
                  label={`AI search: ${documentData.indexing_status}`}
                  color={STATUS_COLOR[documentData.indexing_status] ?? 'default'}
                  size="small"
                  variant="outlined"
                />
              )}
              <Typography variant="body2" color="text.secondary">
                {formatFileSize(documentData.file_size_bytes)} · Uploaded{' '}
                {new Date(documentData.created_at).toLocaleDateString()}
              </Typography>
            </Box>
          </Box>
          <Box sx={{ display: 'flex', gap: 1 }}>
            <Button variant="outlined" onClick={handleDownload}>
              Download
            </Button>
            {documentData.indexing_status === 'failed' && (
              <Button variant="outlined" onClick={handleReindex} disabled={isReindexing}>
                {isReindexing ? 'Indexing...' : 'Retry indexing'}
              </Button>
            )}
            <Button variant="outlined" color="error" onClick={() => setIsDeleteDialogOpen(true)}>
              Delete
            </Button>
          </Box>
        </Box>

        {reindexError && <Alert severity="warning">{reindexError}</Alert>}

        {documentData.indexing_status === 'failed' && documentData.indexing_error && (
          <Alert severity="info">AI search indexing: {documentData.indexing_error}</Alert>
        )}

        {documentData.processing_status === 'failed' && (
          <Alert severity="warning">{documentData.processing_error}</Alert>
        )}

        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Extracted Text
            </Typography>
            {documentData.extracted_text ? (
              <Typography
                variant="body2"
                component="pre"
                sx={{
                  whiteSpace: 'pre-wrap',
                  wordBreak: 'break-word',
                  fontFamily: 'inherit',
                  maxHeight: 480,
                  overflow: 'auto',
                }}
              >
                {documentData.extracted_text}
              </Typography>
            ) : (
              <Typography variant="body2" color="text.secondary">
                No text is available for this document.
              </Typography>
            )}
          </CardContent>
        </Card>
      </Box>

      <Dialog open={isDeleteDialogOpen} onClose={() => setIsDeleteDialogOpen(false)}>
        <DialogTitle>Delete "{documentData.original_filename}"?</DialogTitle>
        <DialogContent>
          <Typography variant="body2">This will permanently delete this document.</Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setIsDeleteDialogOpen(false)}>Cancel</Button>
          <Button color="error" variant="contained" onClick={handleDelete} disabled={isDeleting}>
            {isDeleting ? 'Deleting...' : 'Delete'}
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  )
}

export default DocumentDetailPage