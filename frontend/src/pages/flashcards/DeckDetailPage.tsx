import { useEffect, useState } from 'react'
import type { FormEvent } from 'react'
import { Link as RouterLink, useNavigate, useParams } from 'react-router-dom'
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
  Divider,
  IconButton,
  LinearProgress,
  MenuItem,
  TextField,
  Typography,
} from '@mui/material'
import AutoAwesomeIcon from '@mui/icons-material/AutoAwesome'
import DeleteIcon from '@mui/icons-material/Delete'
import EditIcon from '@mui/icons-material/Edit'
import * as flashcardService from '../../services/flashcardService'
import * as subjectService from '../../services/subjectService'
import type { DeckDetail, Flashcard, MasteryStatus } from '../../types/flashcard'
import type { Subject } from '../../types/subject'

const STATUS_COLOR: Record<MasteryStatus, 'default' | 'warning' | 'success'> = {
  new: 'default',
  learning: 'warning',
  mastered: 'success',
}

const STATUS_LABEL: Record<MasteryStatus, string> = {
  new: 'New',
  learning: 'Learning',
  mastered: 'Mastered',
}

interface FlashcardRowProps {
  card: Flashcard
  onSave: (front: string, back: string) => Promise<void>
  onDelete: () => void
}

function FlashcardRow({ card, onSave, onDelete }: FlashcardRowProps) {
  const [isEditing, setIsEditing] = useState(false)
  const [front, setFront] = useState(card.front)
  const [back, setBack] = useState(card.back)
  const [isSaving, setIsSaving] = useState(false)

  function startEditing() {
    setFront(card.front)
    setBack(card.back)
    setIsEditing(true)
  }

  async function handleSave() {
    setIsSaving(true)
    try {
      await onSave(front, back)
      setIsEditing(false)
    } finally {
      setIsSaving(false)
    }
  }

  return (
    <Card variant="outlined">
      <CardContent>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: 1, mb: 1 }}>
          <Chip
            label={STATUS_LABEL[card.progress.status]}
            color={STATUS_COLOR[card.progress.status]}
            size="small"
          />
          <Box sx={{ display: 'flex', gap: 0.5 }}>
            <IconButton size="small" onClick={startEditing} aria-label="Edit">
              <EditIcon fontSize="small" />
            </IconButton>
            <IconButton size="small" onClick={onDelete} aria-label="Delete">
              <DeleteIcon fontSize="small" />
            </IconButton>
          </Box>
        </Box>

        {isEditing ? (
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
            <TextField
              label="Front"
              value={front}
              onChange={(event) => setFront(event.target.value)}
              multiline
              fullWidth
              disabled={isSaving}
            />
            <TextField
              label="Back"
              value={back}
              onChange={(event) => setBack(event.target.value)}
              multiline
              fullWidth
              disabled={isSaving}
            />
            <Box sx={{ display: 'flex', gap: 1, justifyContent: 'flex-end' }}>
              <Button size="small" onClick={() => setIsEditing(false)} disabled={isSaving}>
                Cancel
              </Button>
              <Button size="small" variant="contained" onClick={handleSave} disabled={isSaving}>
                {isSaving ? 'Saving...' : 'Save'}
              </Button>
            </Box>
          </Box>
        ) : (
          <>
            <Typography variant="body2" sx={{ fontWeight: 600 }}>
              {card.front}
            </Typography>
            <Divider sx={{ my: 1 }} />
            <Typography variant="body2" color="text.secondary">
              {card.back}
            </Typography>
          </>
        )}
      </CardContent>
    </Card>
  )
}

function DeckDetailPage() {
  const { deckId } = useParams<{ deckId: string }>()
  const navigate = useNavigate()

  const [deck, setDeck] = useState<DeckDetail | null>(null)
  const [subjects, setSubjects] = useState<Subject[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const [isEditDialogOpen, setIsEditDialogOpen] = useState(false)
  const [editTitle, setEditTitle] = useState('')
  const [editSubjectId, setEditSubjectId] = useState('')
  const [editDescription, setEditDescription] = useState('')
  const [isSavingEdit, setIsSavingEdit] = useState(false)

  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false)
  const [isDeleting, setIsDeleting] = useState(false)

  const [isGenerateDialogOpen, setIsGenerateDialogOpen] = useState(false)
  const [generateCount, setGenerateCount] = useState(10)
  const [isGenerating, setIsGenerating] = useState(false)
  const [generateError, setGenerateError] = useState<string | null>(null)

  const [newFront, setNewFront] = useState('')
  const [newBack, setNewBack] = useState('')
  const [isAddingCard, setIsAddingCard] = useState(false)

  useEffect(() => {
    if (!deckId) return

    let cancelled = false

    async function fetchDeck() {
      setIsLoading(true)
      setError(null)

      try {
        const data = await flashcardService.getDeck(deckId!)

        if (!cancelled) {
          setDeck(data)
        }
      } catch {
        if (!cancelled) {
          setError('Unable to load this deck.')
        }
      } finally {
        if (!cancelled) {
          setIsLoading(false)
        }
      }
    }

    fetchDeck()
    subjectService
      .listSubjects()
      .then(setSubjects)
      .catch(() => setSubjects([]))

    return () => {
      cancelled = true
    }
  }, [deckId])

  async function reloadDeck() {
    if (!deckId) return
    setIsLoading(true)
    setError(null)
    try {
      const data = await flashcardService.getDeck(deckId)
      setDeck(data)
    } catch {
      setError('Unable to load this deck.')
    } finally {
      setIsLoading(false)
    }
  }

  function openEditDialog() {
    if (!deck) return
    setEditTitle(deck.title)
    setEditSubjectId(deck.subject_id ?? '')
    setEditDescription(deck.description ?? '')
    setIsEditDialogOpen(true)
  }

  async function handleSaveEdit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    if (!deckId) return
    setIsSavingEdit(true)
    try {
      await flashcardService.updateDeck(deckId, {
        title: editTitle,
        subject_id: editSubjectId || null,
        description: editDescription || null,
      })
      setIsEditDialogOpen(false)
      await reloadDeck()
    } finally {
      setIsSavingEdit(false)
    }
  }

  async function handleDeleteDeck() {
    if (!deckId) return
    setIsDeleting(true)
    try {
      await flashcardService.deleteDeck(deckId)
      navigate('/flashcards')
    } finally {
      setIsDeleting(false)
    }
  }

  function openGenerateDialog() {
    setGenerateCount(10)
    setGenerateError(null)
    setIsGenerateDialogOpen(true)
  }

  async function handleGenerate(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    if (!deckId) return
    setGenerateError(null)
    setIsGenerating(true)
    try {
      await flashcardService.generateFlashcards(deckId, { count: generateCount })
      setIsGenerateDialogOpen(false)
      await reloadDeck()
    } catch {
      setGenerateError('Unable to generate flashcards right now. Please try again.')
    } finally {
      setIsGenerating(false)
    }
  }

  async function handleAddCard(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    if (!deckId || !newFront.trim() || !newBack.trim()) return
    setIsAddingCard(true)
    try {
      await flashcardService.addFlashcard(deckId, { front: newFront, back: newBack })
      setNewFront('')
      setNewBack('')
      await reloadDeck()
    } finally {
      setIsAddingCard(false)
    }
  }

  async function handleSaveCard(flashcardId: string, front: string, back: string) {
    if (!deckId) return
    await flashcardService.updateFlashcard(deckId, flashcardId, { front, back })
    await reloadDeck()
  }

  async function handleDeleteCard(flashcardId: string) {
    if (!deckId) return
    await flashcardService.deleteFlashcard(deckId, flashcardId)
    await reloadDeck()
  }

  if (isLoading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '60vh' }}>
        <CircularProgress />
      </Box>
    )
  }

  if (error || !deck) {
    return (
      <Container maxWidth="sm">
        <Alert severity="error" sx={{ mt: 4 }}>
          {error ?? 'Deck not found.'}
        </Alert>
      </Container>
    )
  }

  return (
    <Container maxWidth="md">
      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3, py: 4 }}>
        <Box
          sx={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'flex-start',
            gap: 2,
            flexWrap: 'wrap',
          }}
        >
          <Box>
            <Typography variant="h4" component="h1" sx={{ fontWeight: 600 }}>
              {deck.title}
            </Typography>
            {deck.description && (
              <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                {deck.description}
              </Typography>
            )}
          </Box>
          <Box sx={{ display: 'flex', gap: 1 }}>
            <Button size="small" onClick={openEditDialog}>
              Edit
            </Button>
            <Button size="small" color="error" onClick={() => setIsDeleteDialogOpen(true)}>
              Delete
            </Button>
          </Box>
        </Box>

        <Card>
          <CardContent>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
              <Typography variant="body2">Mastery</Typography>
              <Typography variant="body2" sx={{ fontWeight: 600 }}>
                {deck.mastered_count}/{deck.card_count} cards ({deck.mastery_percentage}%)
              </Typography>
            </Box>
            <LinearProgress
              variant="determinate"
              value={deck.mastery_percentage}
              sx={{ height: 8, borderRadius: 4, mb: 2 }}
            />
            <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
              <Button
                variant="contained"
                component={RouterLink}
                to={`/flashcards/${deck.id}/review`}
                disabled={deck.card_count === 0}
              >
                Review
              </Button>
              <Button variant="outlined" startIcon={<AutoAwesomeIcon />} onClick={openGenerateDialog}>
                Generate flashcards
              </Button>
            </Box>
          </CardContent>
        </Card>

        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Add a flashcard
            </Typography>
            <Box
              component="form"
              onSubmit={handleAddCard}
              sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}
            >
              <TextField
                label="Front"
                value={newFront}
                onChange={(event) => setNewFront(event.target.value)}
                multiline
                fullWidth
                disabled={isAddingCard}
              />
              <TextField
                label="Back"
                value={newBack}
                onChange={(event) => setNewBack(event.target.value)}
                multiline
                fullWidth
                disabled={isAddingCard}
              />
              <Box sx={{ display: 'flex', justifyContent: 'flex-end' }}>
                <Button
                  type="submit"
                  variant="outlined"
                  disabled={isAddingCard || !newFront.trim() || !newBack.trim()}
                >
                  {isAddingCard ? 'Adding...' : 'Add card'}
                </Button>
              </Box>
            </Box>
          </CardContent>
        </Card>

        {deck.flashcards.length === 0 ? (
          <Card>
            <CardContent>
              <Typography variant="body2" color="text.secondary">
                No flashcards yet. Add one manually above or generate a set with AI.
              </Typography>
            </CardContent>
          </Card>
        ) : (
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
            {deck.flashcards.map((card) => (
              <FlashcardRow
                key={card.id}
                card={card}
                onSave={(front, back) => handleSaveCard(card.id, front, back)}
                onDelete={() => handleDeleteCard(card.id)}
              />
            ))}
          </Box>
        )}
      </Box>

      <Dialog open={isEditDialogOpen} onClose={() => setIsEditDialogOpen(false)} fullWidth maxWidth="xs">
        <DialogTitle>Edit deck</DialogTitle>
        <Box component="form" onSubmit={handleSaveEdit}>
          <DialogContent sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
            <TextField
              label="Title"
              value={editTitle}
              onChange={(event) => setEditTitle(event.target.value)}
              required
              fullWidth
              autoFocus
              disabled={isSavingEdit}
            />
            <TextField
              select
              label="Subject (optional)"
              value={editSubjectId}
              onChange={(event) => setEditSubjectId(event.target.value)}
              fullWidth
              disabled={isSavingEdit}
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
              value={editDescription}
              onChange={(event) => setEditDescription(event.target.value)}
              multiline
              minRows={2}
              fullWidth
              disabled={isSavingEdit}
            />
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setIsEditDialogOpen(false)} disabled={isSavingEdit}>
              Cancel
            </Button>
            <Button type="submit" variant="contained" disabled={isSavingEdit}>
              {isSavingEdit ? 'Saving...' : 'Save'}
            </Button>
          </DialogActions>
        </Box>
      </Dialog>

      <Dialog
        open={isGenerateDialogOpen}
        onClose={() => !isGenerating && setIsGenerateDialogOpen(false)}
        fullWidth
        maxWidth="xs"
      >
        <DialogTitle>Generate flashcards</DialogTitle>
        <Box component="form" onSubmit={handleGenerate}>
          <DialogContent sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
            {generateError && <Alert severity="error">{generateError}</Alert>}
            <TextField
              type="number"
              label="Number of flashcards"
              value={generateCount}
              onChange={(event) => setGenerateCount(Number(event.target.value))}
              slotProps={{ htmlInput: { min: 1, max: 20 } }}
              fullWidth
              disabled={isGenerating}
            />
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setIsGenerateDialogOpen(false)} disabled={isGenerating}>
              Cancel
            </Button>
            <Button type="submit" variant="contained" disabled={isGenerating}>
              {isGenerating ? 'Generating...' : 'Generate'}
            </Button>
          </DialogActions>
        </Box>
      </Dialog>

      <Dialog open={isDeleteDialogOpen} onClose={() => setIsDeleteDialogOpen(false)}>
        <DialogTitle>Delete "{deck.title}"?</DialogTitle>
        <DialogContent>
          <Typography variant="body2">
            This will permanently delete this deck and all {deck.card_count} of its flashcards.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setIsDeleteDialogOpen(false)}>Cancel</Button>
          <Button color="error" variant="contained" onClick={handleDeleteDeck} disabled={isDeleting}>
            {isDeleting ? 'Deleting...' : 'Delete'}
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  )
}

export default DeckDetailPage