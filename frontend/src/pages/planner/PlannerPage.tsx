import { useCallback, useEffect, useState } from 'react'
import type { FormEvent } from 'react'
import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  Checkbox,
  Chip,
  CircularProgress,
  Container,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  Divider,
  IconButton,
  MenuItem,
  Tab,
  Tabs,
  TextField,
  Typography,
} from '@mui/material'
import AutoAwesomeIcon from '@mui/icons-material/AutoAwesome'
import DeleteIcon from '@mui/icons-material/Delete'
import EditIcon from '@mui/icons-material/Edit'
import * as plannerService from '../../services/plannerService'
import * as subjectService from '../../services/subjectService'
import type {
  CalendarEntry,
  Deadline,
  GoalStatus,
  PlannerRecommendation,
  SessionStatus,
  StudyGoal,
  StudySession,
} from '../../types/planner'
import type { Subject } from '../../types/subject'

function toDateOnlyString(date: Date): string {
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

function parseDateOnly(value: string): Date {
  const [year, month, day] = value.split('-').map(Number)
  return new Date(year, month - 1, day)
}

function formatDateOnly(value: string): string {
  return parseDateOnly(value).toLocaleDateString(undefined, {
    weekday: 'short',
    month: 'short',
    day: 'numeric',
  })
}

function daysUntil(value: string): number {
  const target = parseDateOnly(value)
  const today = new Date()
  today.setHours(0, 0, 0, 0)
  target.setHours(0, 0, 0, 0)
  return Math.round((target.getTime() - today.getTime()) / (1000 * 60 * 60 * 24))
}

function getPresetRange(preset: 'week' | 'twoWeeks' | 'month'): { start: string; end: string } {
  const today = new Date()
  today.setHours(0, 0, 0, 0)
  const end = new Date(today)
  if (preset === 'week') end.setDate(end.getDate() + 6)
  if (preset === 'twoWeeks') end.setDate(end.getDate() + 13)
  if (preset === 'month') end.setDate(end.getDate() + 29)
  return { start: toDateOnlyString(today), end: toDateOnlyString(end) }
}

function subjectName(subjects: Subject[], subjectId: string | null): string {
  if (!subjectId) return 'General'
  return subjects.find((subject) => subject.id === subjectId)?.name ?? 'Unknown subject'
}

interface SessionFormState {
  title: string
  subjectId: string
  goalId: string
  scheduledDate: string
  startTime: string
  durationMinutes: number
  status: SessionStatus
  notes: string
}

const EMPTY_SESSION_FORM: SessionFormState = {
  title: '',
  subjectId: '',
  goalId: '',
  scheduledDate: toDateOnlyString(new Date()),
  startTime: '',
  durationMinutes: 30,
  status: 'planned',
  notes: '',
}

interface CalendarTabProps {
  subjects: Subject[]
}

function CalendarTab({ subjects }: CalendarTabProps) {
  const [range, setRange] = useState(getPresetRange('twoWeeks'))
  const [entries, setEntries] = useState<CalendarEntry[]>([])
  const [goals, setGoals] = useState<StudyGoal[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const [isSessionDialogOpen, setIsSessionDialogOpen] = useState(false)
  const [editingSessionId, setEditingSessionId] = useState<string | null>(null)
  const [sessionForm, setSessionForm] = useState<SessionFormState>(EMPTY_SESSION_FORM)
  const [isSavingSession, setIsSavingSession] = useState(false)
  const [sessionFormError, setSessionFormError] = useState<string | null>(null)

  const [recommendations, setRecommendations] = useState<PlannerRecommendation[] | null>(null)
  const [isLoadingRecommendations, setIsLoadingRecommendations] = useState(false)
  const [recommendationsError, setRecommendationsError] = useState<string | null>(null)

  const loadEntries = useCallback(async () => {
    setIsLoading(true)
    try {
      const data = await plannerService.getCalendar(range.start, range.end)
      setEntries(data)
      setError(null)
    } catch {
      setError('Unable to load your calendar.')
    } finally {
      setIsLoading(false)
    }
  }, [range.start, range.end])

  useEffect(() => {
    const timeoutId = window.setTimeout(() => {
      void loadEntries()
      plannerService
        .listGoals({ status: 'active' })
        .then(setGoals)
        .catch(() => setGoals([]))
    }, 0)
    return () => window.clearTimeout(timeoutId)
  }, [loadEntries])

  function openCreateDialog() {
    setEditingSessionId(null)
    setSessionForm({ ...EMPTY_SESSION_FORM, scheduledDate: range.start })
    setSessionFormError(null)
    setIsSessionDialogOpen(true)
  }

  function openEditDialog(session: StudySession) {
    setEditingSessionId(session.id)
    setSessionForm({
      title: session.title,
      subjectId: session.subject_id ?? '',
      goalId: session.goal_id ?? '',
      scheduledDate: session.scheduled_date,
      startTime: session.start_time ?? '',
      durationMinutes: session.duration_minutes,
      status: session.status,
      notes: session.notes ?? '',
    })
    setSessionFormError(null)
    setIsSessionDialogOpen(true)
  }

  async function handleSaveSession(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setSessionFormError(null)
    setIsSavingSession(true)
    try {
      const payload = {
        title: sessionForm.title,
        subject_id: sessionForm.subjectId || null,
        goal_id: sessionForm.goalId || null,
        scheduled_date: sessionForm.scheduledDate,
        start_time: sessionForm.startTime || null,
        duration_minutes: sessionForm.durationMinutes,
        notes: sessionForm.notes || null,
      }
      if (editingSessionId) {
        await plannerService.updateSession(editingSessionId, { ...payload, status: sessionForm.status })
      } else {
        await plannerService.createSession(payload)
      }
      setIsSessionDialogOpen(false)
      await loadEntries()
    } catch {
      setSessionFormError('Unable to save this session. Please try again.')
    } finally {
      setIsSavingSession(false)
    }
  }

  async function handleDeleteSession(sessionId: string) {
    await plannerService.deleteSession(sessionId)
    setIsSessionDialogOpen(false)
    await loadEntries()
  }

  async function handleToggleDeadline(deadlineId: string, isCompleted: boolean) {
    await plannerService.updateDeadline(deadlineId, { is_completed: isCompleted })
    await loadEntries()
  }

  async function handleGetRecommendations() {
    setIsLoadingRecommendations(true)
    setRecommendationsError(null)
    try {
      const response = await plannerService.getRecommendations()
      setRecommendations(response.recommendations)
    } catch {
      setRecommendationsError('Unable to generate recommendations right now. Please try again.')
    } finally {
      setIsLoadingRecommendations(false)
    }
  }

  const entriesByDate = new Map<string, CalendarEntry[]>()
  for (const entry of entries) {
    const existing = entriesByDate.get(entry.date) ?? []
    existing.push(entry)
    entriesByDate.set(entry.date, existing)
  }
  const sortedDates = Array.from(entriesByDate.keys()).sort()

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 1 }}>
        <Box sx={{ display: 'flex', gap: 1 }}>
          <Button variant="outlined" size="small" onClick={() => setRange(getPresetRange('week'))}>
            This week
          </Button>
          <Button variant="outlined" size="small" onClick={() => setRange(getPresetRange('twoWeeks'))}>
            Next 2 weeks
          </Button>
          <Button variant="outlined" size="small" onClick={() => setRange(getPresetRange('month'))}>
            Next 30 days
          </Button>
        </Box>
        <Button variant="contained" onClick={openCreateDialog}>
          New session
        </Button>
      </Box>

      <Card>
        <CardContent>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: recommendations ? 2 : 0 }}>
            <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>
              AI recommendations
            </Typography>
            <Button
              size="small"
              startIcon={<AutoAwesomeIcon />}
              onClick={handleGetRecommendations}
              disabled={isLoadingRecommendations}
            >
              {isLoadingRecommendations ? 'Thinking...' : 'Get recommendations'}
            </Button>
          </Box>
          {recommendationsError && (
            <Alert severity="error" sx={{ mt: 1 }}>
              {recommendationsError}
            </Alert>
          )}
          {recommendations && (
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1.5 }}>
              {recommendations.map((recommendation, index) => (
                <Box key={index}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Chip label={recommendation.subject} size="small" />
                    <Typography variant="body2" sx={{ fontWeight: 600 }}>
                      {recommendation.action}
                    </Typography>
                  </Box>
                  <Typography variant="body2" color="text.secondary">
                    {recommendation.reason}
                  </Typography>
                </Box>
              ))}
            </Box>
          )}
        </CardContent>
      </Card>

      {error && <Alert severity="error">{error}</Alert>}

      {isLoading ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', py: 6 }}>
          <CircularProgress />
        </Box>
      ) : sortedDates.length === 0 ? (
        <Card>
          <CardContent>
            <Typography variant="body2" color="text.secondary">
              Nothing scheduled in this range. Add a study session to get started.
            </Typography>
          </CardContent>
        </Card>
      ) : (
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
          {sortedDates.map((dateKey) => (
            <Box key={dateKey}>
              <Typography variant="subtitle2" color="text.secondary" sx={{ mb: 1 }}>
                {formatDateOnly(dateKey)}
              </Typography>
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                {(entriesByDate.get(dateKey) ?? []).map((entry) => (
                  <Card key={`${entry.entry_type}-${entry.id}`} variant="outlined">
                    <CardContent
                      sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: 1 }}
                    >
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
                        {entry.entry_type === 'deadline' ? (
                          <Checkbox
                            checked={entry.is_completed ?? false}
                            onChange={(event) => handleToggleDeadline(entry.id, event.target.checked)}
                          />
                        ) : (
                          <Chip
                            label={entry.status ?? 'planned'}
                            size="small"
                            color={entry.status === 'completed' ? 'success' : 'default'}
                          />
                        )}
                        <Box>
                          <Typography
                            variant="body2"
                            sx={{
                              fontWeight: 600,
                              textDecoration:
                                entry.entry_type === 'deadline' && entry.is_completed ? 'line-through' : 'none',
                            }}
                          >
                            {entry.title}
                          </Typography>
                          <Typography variant="caption" color="text.secondary">
                            {subjectName(subjects, entry.subject_id)}
                            {entry.entry_type === 'session' && entry.start_time ? ` · ${entry.start_time}` : ''}
                            {entry.entry_type === 'session' && entry.duration_minutes
                              ? ` · ${entry.duration_minutes} min`
                              : ''}
                            {entry.entry_type === 'deadline' ? ' · Deadline' : ''}
                          </Typography>
                        </Box>
                      </Box>
                      {entry.entry_type === 'session' && (
                        <IconButton
                          size="small"
                          onClick={() =>
                            openEditDialog({
                              id: entry.id,
                              title: entry.title,
                              subject_id: entry.subject_id,
                              goal_id: null,
                              scheduled_date: entry.date,
                              start_time: entry.start_time,
                              duration_minutes: entry.duration_minutes ?? 30,
                              status: (entry.status as SessionStatus) ?? 'planned',
                              notes: null,
                              created_at: '',
                              updated_at: '',
                            })
                          }
                          aria-label="Edit session"
                        >
                          <EditIcon fontSize="small" />
                        </IconButton>
                      )}
                    </CardContent>
                  </Card>
                ))}
              </Box>
            </Box>
          ))}
        </Box>
      )}

      <Dialog open={isSessionDialogOpen} onClose={() => setIsSessionDialogOpen(false)} fullWidth maxWidth="xs">
        <DialogTitle>{editingSessionId ? 'Edit session' : 'New session'}</DialogTitle>
        <Box component="form" onSubmit={handleSaveSession}>
          <DialogContent sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
            {sessionFormError && <Alert severity="error">{sessionFormError}</Alert>}
            <TextField
              label="Title"
              value={sessionForm.title}
              onChange={(event) => setSessionForm({ ...sessionForm, title: event.target.value })}
              required
              fullWidth
              autoFocus
              disabled={isSavingSession}
            />
            <TextField
              select
              label="Subject (optional)"
              value={sessionForm.subjectId}
              onChange={(event) => setSessionForm({ ...sessionForm, subjectId: event.target.value })}
              fullWidth
              disabled={isSavingSession}
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
              label="Goal (optional)"
              value={sessionForm.goalId}
              onChange={(event) => setSessionForm({ ...sessionForm, goalId: event.target.value })}
              fullWidth
              disabled={isSavingSession}
            >
              <MenuItem value="">No linked goal</MenuItem>
              {goals.map((goal) => (
                <MenuItem key={goal.id} value={goal.id}>
                  {goal.title}
                </MenuItem>
              ))}
            </TextField>
            <TextField
              type="date"
              label="Date"
              value={sessionForm.scheduledDate}
              onChange={(event) => setSessionForm({ ...sessionForm, scheduledDate: event.target.value })}
              required
              fullWidth
              slotProps={{ inputLabel: { shrink: true } }}
              disabled={isSavingSession}
            />
            <TextField
              type="time"
              label="Start time (optional)"
              value={sessionForm.startTime}
              onChange={(event) => setSessionForm({ ...sessionForm, startTime: event.target.value })}
              fullWidth
              slotProps={{ inputLabel: { shrink: true } }}
              disabled={isSavingSession}
            />
            <TextField
              type="number"
              label="Duration (minutes)"
              value={sessionForm.durationMinutes}
              onChange={(event) =>
                setSessionForm({ ...sessionForm, durationMinutes: Number(event.target.value) })
              }
              slotProps={{ htmlInput: { min: 1, max: 600 } }}
              required
              fullWidth
              disabled={isSavingSession}
            />
            {editingSessionId && (
              <TextField
                select
                label="Status"
                value={sessionForm.status}
                onChange={(event) =>
                  setSessionForm({ ...sessionForm, status: event.target.value as SessionStatus })
                }
                fullWidth
                disabled={isSavingSession}
              >
                <MenuItem value="planned">Planned</MenuItem>
                <MenuItem value="completed">Completed</MenuItem>
                <MenuItem value="skipped">Skipped</MenuItem>
              </TextField>
            )}
            <TextField
              label="Notes (optional)"
              value={sessionForm.notes}
              onChange={(event) => setSessionForm({ ...sessionForm, notes: event.target.value })}
              multiline
              minRows={2}
              fullWidth
              disabled={isSavingSession}
            />
          </DialogContent>
          <DialogActions sx={{ justifyContent: editingSessionId ? 'space-between' : 'flex-end', px: 3, pb: 2 }}>
            {editingSessionId && (
              <Button color="error" onClick={() => handleDeleteSession(editingSessionId)} disabled={isSavingSession}>
                Delete
              </Button>
            )}
            <Box sx={{ display: 'flex', gap: 1 }}>
              <Button onClick={() => setIsSessionDialogOpen(false)} disabled={isSavingSession}>
                Cancel
              </Button>
              <Button type="submit" variant="contained" disabled={isSavingSession}>
                {isSavingSession ? 'Saving...' : 'Save'}
              </Button>
            </Box>
          </DialogActions>
        </Box>
      </Dialog>
    </Box>
  )
}

interface GoalFormState {
  title: string
  subjectId: string
  description: string
  targetDate: string
  status: GoalStatus
}

const EMPTY_GOAL_FORM: GoalFormState = {
  title: '',
  subjectId: '',
  description: '',
  targetDate: '',
  status: 'active',
}

interface GoalsTabProps {
  subjects: Subject[]
}

function GoalsTab({ subjects }: GoalsTabProps) {
  const [goals, setGoals] = useState<StudyGoal[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const [isDialogOpen, setIsDialogOpen] = useState(false)
  const [editingGoalId, setEditingGoalId] = useState<string | null>(null)
  const [form, setForm] = useState<GoalFormState>(EMPTY_GOAL_FORM)
  const [isSaving, setIsSaving] = useState(false)
  const [formError, setFormError] = useState<string | null>(null)

  async function loadGoals() {
    setIsLoading(true)
    try {
      const data = await plannerService.listGoals()
      setGoals(data)
      setError(null)
    } catch {
      setError('Unable to load your study goals.')
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    const timeoutId = window.setTimeout(() => {
      void loadGoals()
    }, 0)
    return () => window.clearTimeout(timeoutId)
  }, [])

  function openCreateDialog() {
    setEditingGoalId(null)
    setForm(EMPTY_GOAL_FORM)
    setFormError(null)
    setIsDialogOpen(true)
  }

  function openEditDialog(goal: StudyGoal) {
    setEditingGoalId(goal.id)
    setForm({
      title: goal.title,
      subjectId: goal.subject_id ?? '',
      description: goal.description ?? '',
      targetDate: goal.target_date ?? '',
      status: goal.status,
    })
    setFormError(null)
    setIsDialogOpen(true)
  }

  async function handleSave(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setFormError(null)
    setIsSaving(true)
    try {
      const payload = {
        title: form.title,
        subject_id: form.subjectId || null,
        description: form.description || null,
        target_date: form.targetDate || null,
      }
      if (editingGoalId) {
        await plannerService.updateGoal(editingGoalId, { ...payload, status: form.status })
      } else {
        await plannerService.createGoal(payload)
      }
      setIsDialogOpen(false)
      await loadGoals()
    } catch {
      setFormError('Unable to save this goal. Please try again.')
    } finally {
      setIsSaving(false)
    }
  }

  async function handleDelete(goalId: string) {
    await plannerService.deleteGoal(goalId)
    setIsDialogOpen(false)
    await loadGoals()
  }

  if (isLoading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', py: 6 }}>
        <CircularProgress />
      </Box>
    )
  }

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'flex-end' }}>
        <Button variant="contained" onClick={openCreateDialog}>
          New goal
        </Button>
      </Box>

      {error && <Alert severity="error">{error}</Alert>}

      {goals.length === 0 && !error ? (
        <Card>
          <CardContent>
            <Typography variant="body2" color="text.secondary">
              No study goals yet. Set one to track progress toward something specific.
            </Typography>
          </CardContent>
        </Card>
      ) : (
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
          {goals.map((goal) => (
            <Card key={goal.id} variant="outlined">
              <CardContent>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: 1 }}>
                  <Box>
                    <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>
                      {goal.title}
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      {subjectName(subjects, goal.subject_id)}
                      {goal.target_date
                        ? ` · Target ${formatDateOnly(goal.target_date)} (${daysUntil(goal.target_date)} day(s))`
                        : ''}
                    </Typography>
                  </Box>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Chip
                      label={goal.status}
                      size="small"
                      color={goal.status === 'completed' ? 'success' : goal.status === 'abandoned' ? 'default' : 'primary'}
                    />
                    <IconButton size="small" onClick={() => openEditDialog(goal)} aria-label="Edit goal">
                      <EditIcon fontSize="small" />
                    </IconButton>
                  </Box>
                </Box>
                {goal.description && (
                  <>
                    <Divider sx={{ my: 1 }} />
                    <Typography variant="body2" color="text.secondary">
                      {goal.description}
                    </Typography>
                  </>
                )}
              </CardContent>
            </Card>
          ))}
        </Box>
      )}

      <Dialog open={isDialogOpen} onClose={() => setIsDialogOpen(false)} fullWidth maxWidth="xs">
        <DialogTitle>{editingGoalId ? 'Edit goal' : 'New goal'}</DialogTitle>
        <Box component="form" onSubmit={handleSave}>
          <DialogContent sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
            {formError && <Alert severity="error">{formError}</Alert>}
            <TextField
              label="Title"
              value={form.title}
              onChange={(event) => setForm({ ...form, title: event.target.value })}
              required
              fullWidth
              autoFocus
              disabled={isSaving}
            />
            <TextField
              select
              label="Subject (optional)"
              value={form.subjectId}
              onChange={(event) => setForm({ ...form, subjectId: event.target.value })}
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
              type="date"
              label="Target date (optional)"
              value={form.targetDate}
              onChange={(event) => setForm({ ...form, targetDate: event.target.value })}
              fullWidth
              slotProps={{ inputLabel: { shrink: true } }}
              disabled={isSaving}
            />
            {editingGoalId && (
              <TextField
                select
                label="Status"
                value={form.status}
                onChange={(event) => setForm({ ...form, status: event.target.value as GoalStatus })}
                fullWidth
                disabled={isSaving}
              >
                <MenuItem value="active">Active</MenuItem>
                <MenuItem value="completed">Completed</MenuItem>
                <MenuItem value="abandoned">Abandoned</MenuItem>
              </TextField>
            )}
            <TextField
              label="Description (optional)"
              value={form.description}
              onChange={(event) => setForm({ ...form, description: event.target.value })}
              multiline
              minRows={2}
              fullWidth
              disabled={isSaving}
            />
          </DialogContent>
          <DialogActions sx={{ justifyContent: editingGoalId ? 'space-between' : 'flex-end', px: 3, pb: 2 }}>
            {editingGoalId && (
              <Button color="error" onClick={() => handleDelete(editingGoalId)} disabled={isSaving}>
                Delete
              </Button>
            )}
            <Box sx={{ display: 'flex', gap: 1 }}>
              <Button onClick={() => setIsDialogOpen(false)} disabled={isSaving}>
                Cancel
              </Button>
              <Button type="submit" variant="contained" disabled={isSaving}>
                {isSaving ? 'Saving...' : 'Save'}
              </Button>
            </Box>
          </DialogActions>
        </Box>
      </Dialog>
    </Box>
  )
}

interface DeadlineFormState {
  title: string
  subjectId: string
  dueDate: string
  notes: string
}

const EMPTY_DEADLINE_FORM: DeadlineFormState = {
  title: '',
  subjectId: '',
  dueDate: toDateOnlyString(new Date()),
  notes: '',
}

interface DeadlinesTabProps {
  subjects: Subject[]
}

function DeadlinesTab({ subjects }: DeadlinesTabProps) {
  const [deadlines, setDeadlines] = useState<Deadline[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const [isDialogOpen, setIsDialogOpen] = useState(false)
  const [editingDeadlineId, setEditingDeadlineId] = useState<string | null>(null)
  const [form, setForm] = useState<DeadlineFormState>(EMPTY_DEADLINE_FORM)
  const [isSaving, setIsSaving] = useState(false)
  const [formError, setFormError] = useState<string | null>(null)

  async function loadDeadlines() {
    setIsLoading(true)
    try {
      const data = await plannerService.listDeadlines()
      setDeadlines(data)
      setError(null)
    } catch {
      setError('Unable to load your deadlines.')
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    const timeoutId = window.setTimeout(() => {
      void loadDeadlines()
    }, 0)
    return () => window.clearTimeout(timeoutId)
  }, [])

  function openCreateDialog() {
    setEditingDeadlineId(null)
    setForm(EMPTY_DEADLINE_FORM)
    setFormError(null)
    setIsDialogOpen(true)
  }

  function openEditDialog(deadline: Deadline) {
    setEditingDeadlineId(deadline.id)
    setForm({
      title: deadline.title,
      subjectId: deadline.subject_id ?? '',
      dueDate: deadline.due_date,
      notes: deadline.notes ?? '',
    })
    setFormError(null)
    setIsDialogOpen(true)
  }

  async function handleSave(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setFormError(null)
    setIsSaving(true)
    try {
      const payload = {
        title: form.title,
        subject_id: form.subjectId || null,
        due_date: form.dueDate,
        notes: form.notes || null,
      }
      if (editingDeadlineId) {
        await plannerService.updateDeadline(editingDeadlineId, payload)
      } else {
        await plannerService.createDeadline(payload)
      }
      setIsDialogOpen(false)
      await loadDeadlines()
    } catch {
      setFormError('Unable to save this deadline. Please try again.')
    } finally {
      setIsSaving(false)
    }
  }

  async function handleDelete(deadlineId: string) {
    await plannerService.deleteDeadline(deadlineId)
    setIsDialogOpen(false)
    await loadDeadlines()
  }

  async function handleToggleCompleted(deadlineId: string, isCompleted: boolean) {
    await plannerService.updateDeadline(deadlineId, { is_completed: isCompleted })
    await loadDeadlines()
  }

  if (isLoading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', py: 6 }}>
        <CircularProgress />
      </Box>
    )
  }

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'flex-end' }}>
        <Button variant="contained" onClick={openCreateDialog}>
          New deadline
        </Button>
      </Box>

      {error && <Alert severity="error">{error}</Alert>}

      {deadlines.length === 0 && !error ? (
        <Card>
          <CardContent>
            <Typography variant="body2" color="text.secondary">
              No deadlines yet. Add exam dates or assignment due dates to keep track of them.
            </Typography>
          </CardContent>
        </Card>
      ) : (
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
          {deadlines.map((deadline) => {
            const overdue = !deadline.is_completed && daysUntil(deadline.due_date) < 0
            return (
              <Card key={deadline.id} variant="outlined">
                <CardContent sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <Checkbox
                    checked={deadline.is_completed}
                    onChange={(event) => handleToggleCompleted(deadline.id, event.target.checked)}
                  />
                  <Box sx={{ flexGrow: 1 }}>
                    <Typography
                      variant="body2"
                      sx={{ fontWeight: 600, textDecoration: deadline.is_completed ? 'line-through' : 'none' }}
                    >
                      {deadline.title}
                    </Typography>
                    <Typography variant="caption" color={overdue ? 'error' : 'text.secondary'}>
                      {subjectName(subjects, deadline.subject_id)} · Due {formatDateOnly(deadline.due_date)}
                      {overdue ? ' · Overdue' : ''}
                    </Typography>
                  </Box>
                  <IconButton size="small" onClick={() => openEditDialog(deadline)} aria-label="Edit deadline">
                    <EditIcon fontSize="small" />
                  </IconButton>
                  <IconButton size="small" onClick={() => handleDelete(deadline.id)} aria-label="Delete deadline">
                    <DeleteIcon fontSize="small" />
                  </IconButton>
                </CardContent>
              </Card>
            )
          })}
        </Box>
      )}

      <Dialog open={isDialogOpen} onClose={() => setIsDialogOpen(false)} fullWidth maxWidth="xs">
        <DialogTitle>{editingDeadlineId ? 'Edit deadline' : 'New deadline'}</DialogTitle>
        <Box component="form" onSubmit={handleSave}>
          <DialogContent sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
            {formError && <Alert severity="error">{formError}</Alert>}
            <TextField
              label="Title"
              value={form.title}
              onChange={(event) => setForm({ ...form, title: event.target.value })}
              required
              fullWidth
              autoFocus
              disabled={isSaving}
            />
            <TextField
              select
              label="Subject (optional)"
              value={form.subjectId}
              onChange={(event) => setForm({ ...form, subjectId: event.target.value })}
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
              type="date"
              label="Due date"
              value={form.dueDate}
              onChange={(event) => setForm({ ...form, dueDate: event.target.value })}
              required
              fullWidth
              slotProps={{ inputLabel: { shrink: true } }}
              disabled={isSaving}
            />
            <TextField
              label="Notes (optional)"
              value={form.notes}
              onChange={(event) => setForm({ ...form, notes: event.target.value })}
              multiline
              minRows={2}
              fullWidth
              disabled={isSaving}
            />
          </DialogContent>
          <DialogActions sx={{ justifyContent: editingDeadlineId ? 'space-between' : 'flex-end', px: 3, pb: 2 }}>
            {editingDeadlineId && (
              <Button color="error" onClick={() => handleDelete(editingDeadlineId)} disabled={isSaving}>
                Delete
              </Button>
            )}
            <Box sx={{ display: 'flex', gap: 1 }}>
              <Button onClick={() => setIsDialogOpen(false)} disabled={isSaving}>
                Cancel
              </Button>
              <Button type="submit" variant="contained" disabled={isSaving}>
                {isSaving ? 'Saving...' : 'Save'}
              </Button>
            </Box>
          </DialogActions>
        </Box>
      </Dialog>
    </Box>
  )
}

function PlannerPage() {
  const [activeTab, setActiveTab] = useState(0)
  const [subjects, setSubjects] = useState<Subject[]>([])

  useEffect(() => {
    subjectService
      .listSubjects()
      .then(setSubjects)
      .catch(() => setSubjects([]))
  }, [])

  return (
    <Container maxWidth="md">
      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3, py: 4 }}>
        <Typography variant="h4" component="h1" sx={{ fontWeight: 600 }}>
          Study Planner
        </Typography>

        <Tabs value={activeTab} onChange={(_event, value) => setActiveTab(value)}>
          <Tab label="Calendar" />
          <Tab label="Goals" />
          <Tab label="Deadlines" />
        </Tabs>

        {activeTab === 0 && <CalendarTab subjects={subjects} />}
        {activeTab === 1 && <GoalsTab subjects={subjects} />}
        {activeTab === 2 && <DeadlinesTab subjects={subjects} />}
      </Box>
    </Container>
  )
}

export default PlannerPage