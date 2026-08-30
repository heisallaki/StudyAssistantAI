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
  CircularProgress,
  Container,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  LinearProgress,
  MenuItem,
  TextField,
  Typography,
} from '@mui/material'
import * as flashcardService from '../../services/flashcardService'
import * as subjectService from '../../services/subjectService'
import type { Deck } from '../../types/flashcard'
import type { Subject } from '../../types/subject'

function DecksPage() {
  const [decks, setDecks] = useState<Deck[]>([])
  const [subjects, setSubjects] = useState<Subject[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const [isDialogOpen, setIsDialogOpen] = useState(false)
  const [newTitle, setNewTitle] = useState('')
  const [newSubjectId, setNewSubjectId] = useState('')
  const [newDescription, setNewDescription] = useState('')
  const [isSaving, setIsSaving] = useState(false)
  const [formError, setFormError] = useState<string | null>(null)

  async function loadData() {
    setIsLoading(true)
    try {
      const [decksData, subjectsData] = await Promise.all([
        flashcardService.listDecks(),
        subjectService.listSubjects(),
      ])
      setDecks(decksData)
      setSubjects(subjectsData)
      setError(null)
    } catch {
      setError('Unable to load your flashcard decks.')
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    const timeoutId = window.setTimeout(() => {
      void loadData()
    }, 0)

    return () => window.clearTimeout(timeoutId)
  }, [])

  function openDialog() {
    setNewTitle('')
    setNewSubjectId('')
    setNewDescription('')
    setFormError(null)
    setIsDialogOpen(true)
  }

  async function handleCreate(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setFormError(null)
    setIsSaving(true)
    try {
      await flashcardService.createDeck({
        title: newTitle,
        subject_id: newSubjectId || null,
        description: newDescription || null,
      })
      setIsDialogOpen(false)
      await loadData()
    } catch {
      setFormError('Unable to create this deck. Please try again.')
    } finally {
      setIsSaving(false)
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
            Flashcards
          </Typography>
          <Button variant="contained" onClick={openDialog}>
            New deck
          </Button>
        </Box>

        {error && <Alert severity="error">{error}</Alert>}

        {decks.length === 0 && !error && (
          <Card>
            <CardContent>
              <Typography variant="body2" color="text.secondary">
                No flashcard decks yet. Create one to start adding cards.
              </Typography>
            </CardContent>
          </Card>
        )}

        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
          {decks.map((deck) => (
            <Card key={deck.id}>
              <CardActionArea component={RouterLink} to={`/flashcards/${deck.id}`}>
                <CardContent>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                    <Typography variant="h6">{deck.title}</Typography>
                    <Typography variant="body2" color="text.secondary">
                      {subjectName(deck.subject_id)} · {deck.card_count} cards
                    </Typography>
                  </Box>
                  {deck.card_count > 0 && (
                    <>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
                        <Typography variant="body2" color="text.secondary">
                          {deck.mastered_count}/{deck.card_count} mastered
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          {deck.mastery_percentage}%
                        </Typography>
                      </Box>
                      <LinearProgress
                        variant="determinate"
                        value={deck.mastery_percentage}
                        sx={{ height: 6, borderRadius: 3 }}
                      />
                    </>
                  )}
                </CardContent>
              </CardActionArea>
            </Card>
          ))}
        </Box>
      </Box>

      <Dialog open={isDialogOpen} onClose={() => !isSaving && setIsDialogOpen(false)} fullWidth maxWidth="xs">
        <DialogTitle>New deck</DialogTitle>
        <Box component="form" onSubmit={handleCreate}>
          <DialogContent sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
            {formError && <Alert severity="error">{formError}</Alert>}
            <TextField
              label="Title"
              value={newTitle}
              onChange={(event) => setNewTitle(event.target.value)}
              required
              fullWidth
              autoFocus
              disabled={isSaving}
            />
            <TextField
              select
              label="Subject (optional)"
              value={newSubjectId}
              onChange={(event) => setNewSubjectId(event.target.value)}
              fullWidth
              disabled={isSaving}
            >
              <MenuItem value="">General (no subject)</MenuItem>
              {subjects.map((subject) => (
                <MenuItem key={subject.id} value={subject.id}>
                  {subject.name}
                </MenuItem>
              ))}
            </TextField>
            <TextField
              label="Description"
              value={newDescription}
              onChange={(event) => setNewDescription(event.target.value)}
              multiline
              minRows={2}
              fullWidth
              disabled={isSaving}
            />
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setIsDialogOpen(false)} disabled={isSaving}>
              Cancel
            </Button>
            <Button type="submit" variant="contained" disabled={isSaving || !newTitle.trim()}>
              {isSaving ? 'Creating...' : 'Create'}
            </Button>
          </DialogActions>
        </Box>
      </Dialog>
    </Container>
  )
}

export default DecksPage