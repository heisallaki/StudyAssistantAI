import { useEffect, useState } from 'react'
import type { FormEvent } from 'react'
import { Link as RouterLink } from 'react-router-dom'
import {
  Alert,
  Box,
  Button,
  Card,
  CardActionArea,
  CardContent,
  Chip,
  CircularProgress,
  Container,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  IconButton,
  MenuItem,
  TextField,
  Typography,
} from '@mui/material'
import DeleteIcon from '@mui/icons-material/Delete'
import * as tutorService from '../../services/tutorService'
import * as subjectService from '../../services/subjectService'
import type { Conversation, ConversationMode, ExplanationLevel } from '../../types/tutor'
import type { Subject } from '../../types/subject'

function ConversationsPage() {
  const [conversations, setConversations] = useState<Conversation[]>([])
  const [subjects, setSubjects] = useState<Subject[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const [isDialogOpen, setIsDialogOpen] = useState(false)
  const [newSubjectId, setNewSubjectId] = useState('')
  const [newMode, setNewMode] = useState<ConversationMode>('tutor')
  const [newLevel, setNewLevel] = useState<ExplanationLevel>('intermediate')
  const [isCreating, setIsCreating] = useState(false)

  const [deleteTarget, setDeleteTarget] = useState<Conversation | null>(null)
  const [isDeleting, setIsDeleting] = useState(false)
  const [deleteError, setDeleteError] = useState<string | null>(null)

  useEffect(() => {
    Promise.all([tutorService.listConversations(), subjectService.listSubjects()])
      .then(([conversationsData, subjectsData]) => {
        setConversations(conversationsData)
        setSubjects(subjectsData)
      })
      .catch(() => setError('Unable to load your conversations.'))
      .finally(() => setIsLoading(false))
  }, [])

  async function handleCreate(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setIsCreating(true)
    try {
      const conversation = await tutorService.createConversation({
        subject_id: newSubjectId || null,
        mode: newMode,
        explanation_level: newLevel,
      })
      window.location.href = `/tutor/${conversation.id}`
    } catch {
      setError('Unable to start a new conversation.')
      setIsCreating(false)
    }
  }

  function openDeleteDialog(conversation: Conversation) {
    setDeleteTarget(conversation)
    setDeleteError(null)
  }

  async function handleConfirmDelete() {
    if (!deleteTarget) return
    setIsDeleting(true)
    setDeleteError(null)
    try {
      await tutorService.deleteConversation(deleteTarget.id)
      setConversations((current) => current.filter((item) => item.id !== deleteTarget.id))
      setDeleteTarget(null)
    } catch {
      setDeleteError('Unable to delete this conversation. Please try again.')
    } finally {
      setIsDeleting(false)
    }
  }

  function subjectName(subjectId: string | null): string {
    if (!subjectId) return 'General'
    return subjects.find((subject) => subject.id === subjectId)?.name ?? 'General'
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
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Typography variant="h4" component="h1" sx={{ fontWeight: 600 }}>
            AI Tutor
          </Typography>
          <Button variant="contained" onClick={() => setIsDialogOpen(true)}>
            New conversation
          </Button>
        </Box>

        {error && <Alert severity="error">{error}</Alert>}

        {conversations.length === 0 ? (
          <Typography variant="body2" color="text.secondary">
            No conversations yet. Start one to get help from your AI tutor.
          </Typography>
        ) : (
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
            {conversations.map((conversation) => (
              <Card key={conversation.id}>
                <CardActionArea component={RouterLink} to={`/tutor/${conversation.id}`}>
                  <CardContent>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 1 }}>
                      <Typography variant="h6">{conversation.title}</Typography>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <Chip label={subjectName(conversation.subject_id)} size="small" variant="outlined" />
                        <Chip
                          label={conversation.mode === 'socratic' ? 'Socratic' : 'Direct'}
                          size="small"
                          color={conversation.mode === 'socratic' ? 'secondary' : 'default'}
                        />
                        <IconButton
                          size="small"
                          aria-label="Delete conversation"
                          onClick={(event) => {
                            event.preventDefault()
                            event.stopPropagation()
                            openDeleteDialog(conversation)
                          }}
                        >
                          <DeleteIcon fontSize="small" />
                        </IconButton>
                      </Box>
                    </Box>
                    <Typography variant="caption" color="text.secondary">
                      Updated {new Date(conversation.updated_at).toLocaleString()}
                    </Typography>
                  </CardContent>
                </CardActionArea>
              </Card>
            ))}
          </Box>
        )}
      </Box>

      <Dialog open={isDialogOpen} onClose={() => setIsDialogOpen(false)} fullWidth maxWidth="xs">
        <DialogTitle>Start a new conversation</DialogTitle>
        <Box component="form" onSubmit={handleCreate}>
          <DialogContent sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
            <TextField
              select
              label="Subject"
              value={newSubjectId}
              onChange={(event) => setNewSubjectId(event.target.value)}
              fullWidth
            >
              <MenuItem value="">General</MenuItem>
              {subjects.map((subject) => (
                <MenuItem key={subject.id} value={subject.id}>
                  {subject.name}
                </MenuItem>
              ))}
            </TextField>
            <TextField
              select
              label="Mode"
              value={newMode}
              onChange={(event) => setNewMode(event.target.value as ConversationMode)}
              fullWidth
            >
              <MenuItem value="tutor">Direct</MenuItem>
              <MenuItem value="socratic">Socratic</MenuItem>
            </TextField>
            <TextField
              select
              label="Explanation level"
              value={newLevel}
              onChange={(event) => setNewLevel(event.target.value as ExplanationLevel)}
              fullWidth
            >
              <MenuItem value="beginner">Beginner</MenuItem>
              <MenuItem value="intermediate">Intermediate</MenuItem>
              <MenuItem value="advanced">Advanced</MenuItem>
            </TextField>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setIsDialogOpen(false)}>Cancel</Button>
            <Button type="submit" variant="contained" disabled={isCreating}>
              {isCreating ? 'Starting...' : 'Start'}
            </Button>
          </DialogActions>
        </Box>
      </Dialog>

      <Dialog open={deleteTarget !== null} onClose={() => !isDeleting && setDeleteTarget(null)}>
        <DialogTitle>Delete "{deleteTarget?.title}"?</DialogTitle>
        <DialogContent sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
          {deleteError && <Alert severity="error">{deleteError}</Alert>}
          <Typography variant="body2">
            This will permanently delete this conversation and all of its messages. This cannot be undone.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteTarget(null)} disabled={isDeleting}>
            Cancel
          </Button>
          <Button color="error" variant="contained" onClick={handleConfirmDelete} disabled={isDeleting}>
            {isDeleting ? 'Deleting...' : 'Delete'}
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  )
}

export default ConversationsPage