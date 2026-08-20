import { useEffect, useState } from 'react'
import type { ChangeEvent } from 'react'
import { Link as RouterLink } from 'react-router-dom'
import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  Chip,
  CircularProgress,
  Container,
  IconButton,
  MenuItem,
  TextField,
  Typography,
} from '@mui/material'
import DeleteIcon from '@mui/icons-material/Delete'
import DownloadIcon from '@mui/icons-material/Download'
import UploadFileIcon from '@mui/icons-material/UploadFile'
import * as documentService from '../../services/documentService'
import * as subjectService from '../../services/subjectService'
import type { Document as StudyDocument } from '../../types/document'
import type { Subject } from '../../types/subject'

function formatFileSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}

const STATUS_COLOR: Record<string, 'success' | 'warning' | 'default'> = {
  processed: 'success',
  failed: 'warning',
  pending: 'default',
  indexed: 'success',
  not_applicable: 'default',
}

function DocumentsPage() {
  const [documents, setDocuments] = useState<StudyDocument[]>([])
  const [subjects, setSubjects] = useState<Subject[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const [selectedSubjectId, setSelectedSubjectId] = useState('')
  const [isUploading, setIsUploading] = useState(false)
  const [uploadMessage, setUploadMessage] = useState<string | null>(null)
  const [uploadError, setUploadError] = useState<string | null>(null)

  useEffect(() => {
  let cancelled = false

  async function initializePage() {
    try {
      const [documentsData, subjectsData] = await Promise.all([
        documentService.listDocuments(),
        subjectService.listSubjects(),
      ])

      if (cancelled) return

      setDocuments(documentsData)
      setSubjects(subjectsData)
    } catch {
      if (!cancelled) {
        setError('Unable to load your documents.')
      }
    } finally {
      if (!cancelled) {
        setIsLoading(false)
      }
    }
  }

  initializePage()

  return () => {
    cancelled = true
  }
}, [])

async function loadData() {
  try {
    const [documentsData, subjectsData] = await Promise.all([
      documentService.listDocuments(),
      subjectService.listSubjects(),
    ])

    setDocuments(documentsData)
    setSubjects(subjectsData)
  } catch {
    setError('Unable to load your documents.')
  }
}

  async function handleFileSelected(event: ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0]
    event.target.value = ''
    if (!file) return

    setUploadError(null)
    setUploadMessage(null)
    setIsUploading(true)
    try {
      const uploaded = await documentService.uploadDocument(file, selectedSubjectId || undefined)
      if (uploaded.processing_status === 'processed') {
        setUploadMessage(`"${uploaded.original_filename}" uploaded and processed successfully.`)
      } else {
        setUploadMessage(
          `"${uploaded.original_filename}" uploaded, but text extraction failed: ${uploaded.processing_error}`,
        )
      }
      loadData()
    } catch {
      setUploadError('Unable to upload this file. Please check the file type and size and try again.')
    } finally {
      setIsUploading(false)
    }
  }

  async function handleDelete(documentId: string) {
    await documentService.deleteDocument(documentId)
    loadData()
  }

  async function handleDownload(doc: StudyDocument) {
    await documentService.downloadDocument(doc.id, doc.original_filename)
  }

  function subjectName(subjectId: string | null): string {
    if (!subjectId) return 'No subject'
    return subjects.find((subject) => subject.id === subjectId)?.name ?? 'Unknown subject'
  }

  if (isLoading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '60vh' }}>
        <CircularProgress />
      </Box>
    )
  }

  return (
    <Container maxWidth="md">
      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3, py: 4 }}>
        <Typography variant="h4" component="h1" sx={{ fontWeight: 600 }}>
          Documents
        </Typography>

        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Upload a document
            </Typography>
            {uploadError && (
              <Alert severity="error" sx={{ mb: 2 }}>
                {uploadError}
              </Alert>
            )}
            {uploadMessage && (
              <Alert severity="info" sx={{ mb: 2 }}>
                {uploadMessage}
              </Alert>
            )}
            <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap', alignItems: 'center' }}>
              <TextField
                select
                label="Subject (optional)"
                value={selectedSubjectId}
                onChange={(event) => setSelectedSubjectId(event.target.value)}
                size="small"
                sx={{ minWidth: 220 }}
              >
                <MenuItem value="">No subject</MenuItem>
                {subjects.map((subject) => (
                  <MenuItem key={subject.id} value={subject.id}>
                    {subject.name}
                  </MenuItem>
                ))}
              </TextField>
              <Button variant="contained" component="label" startIcon={<UploadFileIcon />} disabled={isUploading}>
                {isUploading ? 'Uploading...' : 'Choose file'}
                <input type="file" hidden accept=".pdf,.txt,.md" onChange={handleFileSelected} />
              </Button>
              <Typography variant="caption" color="text.secondary">
                PDF, TXT, or MD — up to 20 MB
              </Typography>
            </Box>
          </CardContent>
        </Card>

        {error && <Alert severity="error">{error}</Alert>}

        {documents.length === 0 && !error && (
          <Card>
            <CardContent>
              <Typography variant="body2" color="text.secondary">
                No documents yet. Upload your study materials to get started.
              </Typography>
            </CardContent>
          </Card>
        )}

        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
          {documents.map((doc) => (
            <Card key={doc.id}>
              <CardContent>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: 2 }}>
                  <Box sx={{ minWidth: 0 }}>
                    <Typography
                      variant="h6"
                      component={RouterLink}
                      to={`/documents/${doc.id}`}
                      sx={{ textDecoration: 'none', color: 'inherit', display: 'block' }}
                    >
                      {doc.original_filename}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      {subjectName(doc.subject_id)} · {formatFileSize(doc.file_size_bytes)}
                    </Typography>
                  </Box>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Chip label={doc.processing_status} color={STATUS_COLOR[doc.processing_status] ?? 'default'} size="small" />
                    {doc.indexing_status !== 'not_applicable' && (
                      <Chip
                        label={`AI: ${doc.indexing_status}`}
                        color={STATUS_COLOR[doc.indexing_status] ?? 'default'}
                        size="small"
                        variant="outlined"
                      />
                    )}
                    <IconButton onClick={() => handleDownload(doc)} aria-label="Download">
                      <DownloadIcon fontSize="small" />
                    </IconButton>
                    <IconButton onClick={() => handleDelete(doc.id)} aria-label="Delete">
                      <DeleteIcon fontSize="small" />
                    </IconButton>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          ))}
        </Box>
      </Box>
    </Container>
  )
}

export default DocumentsPage