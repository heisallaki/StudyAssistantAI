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
  LinearProgress,
  MenuItem,
  TextField,
  Typography,
} from '@mui/material'
import * as subjectService from '../../services/subjectService'
import type { Subject, SubjectPriority } from '../../types/subject'

const PRIORITY_COLOR: Record<SubjectPriority, 'default' | 'warning' | 'error'> = {
  low: 'default',
  medium: 'warning',
  high: 'error',
}

const PRIORITY_LABEL: Record<SubjectPriority, string> = {
  low: 'Low priority',
  medium: 'Medium priority',
  high: 'High priority',
}

function SubjectsListPage() {
  const [subjects, setSubjects] = useState<Subject[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const [isDialogOpen, setIsDialogOpen] = useState(false)
  const [name, setName] = useState('')
  const [description, setDescription] = useState('')
  const [priority, setPriority] = useState<SubjectPriority>('medium')
  const [isSaving, setIsSaving] = useState(false)
  const [formError, setFormError] = useState<string | null>(null)

  useEffect(() => {
    let cancelled = false

    async function fetchSubjects() {
      setIsLoading(true)
      setError(null)

      try {
        const data = await subjectService.listSubjects()

        if (!cancelled) {
          setSubjects(data)
        }
      } catch {
        if (!cancelled) {
          setError('Unable to load your subjects.')
        }
      } finally {
        if (!cancelled) {
          setIsLoading(false)
        }
      }
    }

    fetchSubjects()

    return () => {
      cancelled = true
    }
  }, [])

  async function reloadSubjects() {
    setIsLoading(true)
    setError(null)

    try {
      const data = await subjectService.listSubjects()
      setSubjects(data)
    } catch {
      setError('Unable to load your subjects.')
    } finally {
      setIsLoading(false)
    }
  }

  async function handleCreate(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setFormError(null)
    setIsSaving(true)

    try {
      await subjectService.createSubject({
        name,
        description: description || null,
        priority,
      })

      setIsDialogOpen(false)
      setName('')
      setDescription('')
      setPriority('medium')
      await reloadSubjects()
    } catch {
      setFormError('Unable to create subject. Please try again.')
    } finally {
      setIsSaving(false)
    }
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
            Subjects
          </Typography>

          <Button variant="contained" onClick={() => setIsDialogOpen(true)}>
            New subject
          </Button>
        </Box>

        {error && <Alert severity="error">{error}</Alert>}

        {subjects.length === 0 && !error && (
          <Card>
            <CardContent>
              <Typography variant="body2" color="text.secondary">
                You haven't added any subjects yet. Create one to start tracking your topics and progress.
              </Typography>
            </CardContent>
          </Card>
        )}

        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
          {subjects.map((subject) => (
            <Card key={subject.id}>
              <CardActionArea component={RouterLink} to={`/subjects/${subject.id}`}>
                <CardContent>
                  <Box
                    sx={{
                      display: 'flex',
                      justifyContent: 'space-between',
                      alignItems: 'center',
                      mb: 1,
                    }}
                  >
                    <Typography variant="h6">{subject.name}</Typography>

                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <Chip
                        label={PRIORITY_LABEL[subject.priority]}
                        color={PRIORITY_COLOR[subject.priority]}
                        size="small"
                        variant="outlined"
                      />
                      <Typography variant="body2" color="text.secondary">
                        {subject.completed_topic_count}/{subject.topic_count} topics
                      </Typography>
                    </Box>
                  </Box>

                  {subject.description && (
                    <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                      {subject.description}
                    </Typography>
                  )}

                  <LinearProgress
                    variant="determinate"
                    value={subject.progress_percentage}
                    sx={{ height: 6, borderRadius: 3 }}
                  />
                </CardContent>
              </CardActionArea>
            </Card>
          ))}
        </Box>
      </Box>

      <Dialog
        open={isDialogOpen}
        onClose={() => setIsDialogOpen(false)}
        fullWidth
        maxWidth="xs"
      >
        <DialogTitle>New subject</DialogTitle>

        <Box component="form" onSubmit={handleCreate}>
          <DialogContent sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
            {formError && <Alert severity="error">{formError}</Alert>}

            <TextField
              label="Name"
              value={name}
              onChange={(event) => setName(event.target.value)}
              required
              fullWidth
              autoFocus
            />

            <TextField
              label="Description"
              value={description}
              onChange={(event) => setDescription(event.target.value)}
              multiline
              minRows={2}
              fullWidth
            />

            <TextField
              select
              label="Priority"
              value={priority}
              onChange={(event) => setPriority(event.target.value as SubjectPriority)}
              fullWidth
            >
              <MenuItem value="low">Low</MenuItem>
              <MenuItem value="medium">Medium</MenuItem>
              <MenuItem value="high">High</MenuItem>
            </TextField>
          </DialogContent>

          <DialogActions>
            <Button onClick={() => setIsDialogOpen(false)}>
              Cancel
            </Button>

            <Button type="submit" variant="contained" disabled={isSaving}>
              {isSaving ? 'Creating...' : 'Create'}
            </Button>
          </DialogActions>
        </Box>
      </Dialog>
    </Container>
  )
}

export default SubjectsListPage