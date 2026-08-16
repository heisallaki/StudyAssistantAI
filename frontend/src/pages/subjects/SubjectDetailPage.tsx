import { useEffect, useState } from 'react'
import type { FormEvent } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  Checkbox,
  CircularProgress,
  Container,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  IconButton,
  LinearProgress,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  TextField,
  Typography,
} from '@mui/material'
import DeleteIcon from '@mui/icons-material/Delete'
import * as subjectService from '../../services/subjectService'
import type { SubjectDetail } from '../../types/subject'

function SubjectDetailPage() {
  const { subjectId } = useParams<{ subjectId: string }>()
  const navigate = useNavigate()

  const [subject, setSubject] = useState<SubjectDetail | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const [newTopicTitle, setNewTopicTitle] = useState('')
  const [isAddingTopic, setIsAddingTopic] = useState(false)

  const [isEditDialogOpen, setIsEditDialogOpen] = useState(false)
  const [editName, setEditName] = useState('')
  const [editDescription, setEditDescription] = useState('')
  const [isSavingEdit, setIsSavingEdit] = useState(false)

  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false)
  const [isDeleting, setIsDeleting] = useState(false)

  useEffect(() => {
  if (!subjectId) return

  let cancelled = false

  async function fetchSubject() {
    setIsLoading(true)
    setError(null)

    try {
      const data = await subjectService.getSubject(subjectId!)

      if (!cancelled) {
        setSubject(data)
      }
    } catch {
      if (!cancelled) {
        setError('Unable to load this subject.')
      }
    } finally {
      if (!cancelled) {
        setIsLoading(false)
      }
    }
  }

  fetchSubject()

  return () => {
    cancelled = true
  }
}, [subjectId])

  async function handleToggleTopic(topicId: string, isCompleted: boolean) {
    if (!subjectId) return
    await subjectService.updateTopic(subjectId, topicId, { is_completed: isCompleted })
    await reloadSubject()
  }

  async function handleDeleteTopic(topicId: string) {
    if (!subjectId) return
    await subjectService.deleteTopic(subjectId, topicId)
    await reloadSubject()
  }

  async function handleAddTopic(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    if (!subjectId || !newTopicTitle.trim()) return
    setIsAddingTopic(true)
    try {
      await subjectService.createTopic(subjectId, { title: newTopicTitle.trim() })
      setNewTopicTitle('')
      await reloadSubject()
    } finally {
      setIsAddingTopic(false)
    }
  }

  function openEditDialog() {
    if (!subject) return
    setEditName(subject.name)
    setEditDescription(subject.description ?? '')
    setIsEditDialogOpen(true)
  }

  async function handleSaveEdit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    if (!subjectId) return
    setIsSavingEdit(true)
    try {
      await subjectService.updateSubject(subjectId, {
        name: editName,
        description: editDescription || null,
      })
      setIsEditDialogOpen(false)
      await reloadSubject()
    } finally {
      setIsSavingEdit(false)
    }
  }

  async function handleDeleteSubject() {
    if (!subjectId) return
    setIsDeleting(true)
    try {
      await subjectService.deleteSubject(subjectId)
      navigate('/subjects')
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

  if (error || !subject) {
    return (
      <Container maxWidth="sm">
        <Alert severity="error" sx={{ mt: 4 }}>
          {error ?? 'Subject not found.'}
        </Alert>
      </Container>
    )
  }
  async function reloadSubject() {
  if (!subjectId) return

  setIsLoading(true)
  setError(null)

  try {
    const data = await subjectService.getSubject(subjectId)
    setSubject(data)
  } catch {
    setError('Unable to load this subject.')
  } finally {
    setIsLoading(false)
  }
}

  return (
    <Container maxWidth="sm">
      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3, py: 4 }}>
        <Box>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: 2 }}>
            <Typography variant="h4" component="h1" sx={{ fontWeight: 600 }}>
              {subject.name}
            </Typography>
            <Box sx={{ display: 'flex', gap: 1 }}>
              <Button size="small" onClick={openEditDialog}>
                Edit
              </Button>
              <Button size="small" color="error" onClick={() => setIsDeleteDialogOpen(true)}>
                Delete
              </Button>
            </Box>
          </Box>
          {subject.description && (
            <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
              {subject.description}
            </Typography>
          )}
        </Box>

        <Card>
          <CardContent>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
              <Typography variant="body2">Progress</Typography>
              <Typography variant="body2" sx={{ fontWeight: 600 }}>
                {subject.completed_topic_count}/{subject.topic_count} topics ({subject.progress_percentage}%)
              </Typography>
            </Box>
            <LinearProgress
              variant="determinate"
              value={subject.progress_percentage}
              sx={{ height: 8, borderRadius: 4 }}
            />
          </CardContent>
        </Card>

        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Topics
            </Typography>
            {subject.topics.length === 0 ? (
              <Typography variant="body2" color="text.secondary">
                No topics yet. Add your first topic below.
              </Typography>
            ) : (
              <List disablePadding>
                {subject.topics.map((topic) => (
                  <ListItem
                    key={topic.id}
                    disablePadding
                    secondaryAction={
                      <IconButton edge="end" onClick={() => handleDeleteTopic(topic.id)} aria-label="Delete topic">
                        <DeleteIcon fontSize="small" />
                      </IconButton>
                    }
                  >
                    <ListItemIcon sx={{ minWidth: 40 }}>
                      <Checkbox
                        edge="start"
                        checked={topic.is_completed}
                        onChange={(event) => handleToggleTopic(topic.id, event.target.checked)}
                      />
                    </ListItemIcon>
                    <ListItemText
                      primary={topic.title}
                      sx={{ textDecoration: topic.is_completed ? 'line-through' : 'none' }}
                    />
                  </ListItem>
                ))}
              </List>
            )}
            <Box component="form" onSubmit={handleAddTopic} sx={{ display: 'flex', gap: 1, mt: 2 }}>
              <TextField
                label="Add a topic"
                value={newTopicTitle}
                onChange={(event) => setNewTopicTitle(event.target.value)}
                size="small"
                fullWidth
              />
              <Button type="submit" variant="outlined" disabled={isAddingTopic || !newTopicTitle.trim()}>
                Add
              </Button>
            </Box>
          </CardContent>
        </Card>
      </Box>

      <Dialog open={isEditDialogOpen} onClose={() => setIsEditDialogOpen(false)} fullWidth maxWidth="xs">
        <DialogTitle>Edit subject</DialogTitle>
        <Box component="form" onSubmit={handleSaveEdit}>
          <DialogContent sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
            <TextField
              label="Name"
              value={editName}
              onChange={(event) => setEditName(event.target.value)}
              required
              fullWidth
              autoFocus
            />
            <TextField
              label="Description"
              value={editDescription}
              onChange={(event) => setEditDescription(event.target.value)}
              multiline
              minRows={2}
              fullWidth
            />
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setIsEditDialogOpen(false)}>Cancel</Button>
            <Button type="submit" variant="contained" disabled={isSavingEdit}>
              {isSavingEdit ? 'Saving...' : 'Save'}
            </Button>
          </DialogActions>
        </Box>
      </Dialog>

      <Dialog open={isDeleteDialogOpen} onClose={() => setIsDeleteDialogOpen(false)}>
        <DialogTitle>Delete "{subject.name}"?</DialogTitle>
        <DialogContent>
          <Typography variant="body2">
            This will permanently delete this subject and all {subject.topic_count} of its topics.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setIsDeleteDialogOpen(false)}>Cancel</Button>
          <Button color="error" variant="contained" onClick={handleDeleteSubject} disabled={isDeleting}>
            {isDeleting ? 'Deleting...' : 'Delete'}
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  )
}

export default SubjectDetailPage