import { useEffect, useState } from 'react'
import type { FormEvent } from 'react'
import { Link as RouterLink, useNavigate } from 'react-router-dom'
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
  MenuItem,
  TextField,
  Typography,
} from '@mui/material'
import * as tutorService from '../../services/tutorService'
import * as subjectService from '../../services/subjectService'
import type { Conversation, ConversationMode, ExplanationLevel } from '../../types/tutor'
import type { Subject } from '../../types/subject'

function ConversationsPage() {
  const navigate = useNavigate()
  const [conversations, setConversations] = useState<Conversation[]>([])
  const [subjects, setSubjects] = useState<Subject[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const [isDialogOpen, setIsDialogOpen] = useState(false)
  const [newSubjectId, setNewSubjectId] = useState('')
  const [newMode, setNewMode] = useState<ConversationMode>('tutor')
  const [newLevel, setNewLevel] = useState<ExplanationLevel>('intermediate')
  const [isCreating, setIsCreating] = useState(false)

  useEffect(() => {
  let isMounted = true

  async function loadData() {
    try {
      const [conversationsData, subjectsData] = await Promise.all([
        tutorService.listConversations(),
        subjectService.listSubjects(),
      ])

      if (!isMounted) return

      setConversations(conversationsData)
      setSubjects(subjectsData)
    } catch {
      if (!isMounted) return

      setError('Unable to load your conversations.')
    } finally {
      if (isMounted) {
        setIsLoading(false)
      }
    }
  }

  loadData()

  return () => {
    isMounted = false
  }
}, [])

  function openDialog() {
    setNewSubjectId('')
    setNewMode('tutor')
    setNewLevel('intermediate')
    setIsDialogOpen(true)
  }

  async function handleCreate(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setIsCreating(true)
    try {
      const conversation = await tutorService.createConversation({
        subject_id: newSubjectId || null,
        mode: newMode,
        explanation_level: newLevel,
      })
      navigate(`/tutor/${conversation.id}`)
    } finally {
      setIsCreating(false)
    }
  }

  function subjectName(subjectId: string | null): string {
    if (!subjectId) return 'General'
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
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Typography variant="h4" component="h1" sx={{ fontWeight: 600 }}>
            AI Tutor
          </Typography>
          <Button variant="contained" onClick={openDialog}>
            New conversation
          </Button>
        </Box>

        {error && <Alert severity="error">{error}</Alert>}

        {conversations.length === 0 && !error && (
          <Card>
            <CardContent>
              <Typography variant="body2" color="text.secondary">
                No conversations yet. Start one to ask the AI tutor a question.
              </Typography>
            </CardContent>
          </Card>
        )}

        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
          {conversations.map((conversation) => (
            <Card key={conversation.id}>
              <CardActionArea component={RouterLink} to={`/tutor/${conversation.id}`}>
                <CardContent>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 1 }}>
                    <Typography variant="h6">{conversation.title}</Typography>
                    <Box sx={{ display: 'flex', gap: 1 }}>
                      <Chip label={subjectName(conversation.subject_id)} size="small" variant="outlined" />
                      <Chip
                        label={conversation.mode === 'socratic' ? 'Socratic' : 'Direct'}
                        size="small"
                        color={conversation.mode === 'socratic' ? 'secondary' : 'default'}
                      />
                    </Box>
                  </Box>
                </CardContent>
              </CardActionArea>
            </Card>
          ))}
        </Box>
      </Box>

      <Dialog open={isDialogOpen} onClose={() => setIsDialogOpen(false)} fullWidth maxWidth="xs">
        <DialogTitle>New conversation</DialogTitle>
        <Box component="form" onSubmit={handleCreate}>
          <DialogContent sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
            <TextField
              select
              label="Subject (optional)"
              value={newSubjectId}
              onChange={(event) => setNewSubjectId(event.target.value)}
              fullWidth
            >
              <MenuItem value="">General (no subject)</MenuItem>
              {subjects.map((subject) => (
                <MenuItem key={subject.id} value={subject.id}>
                  {subject.name}
                </MenuItem>
              ))}
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
            <TextField
              select
              label="Mode"
              value={newMode}
              onChange={(event) => setNewMode(event.target.value as ConversationMode)}
              fullWidth
              helperText={
                newMode === 'socratic'
                  ? 'The tutor will guide you with questions instead of giving direct answers.'
                  : 'The tutor will answer your questions directly.'
              }
            >
              <MenuItem value="tutor">Direct answers</MenuItem>
              <MenuItem value="socratic">Socratic (guided questions)</MenuItem>
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
    </Container>
  )
}

export default ConversationsPage