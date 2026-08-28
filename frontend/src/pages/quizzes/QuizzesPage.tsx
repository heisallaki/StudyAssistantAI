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
  Checkbox,
  Chip,
  CircularProgress,
  Container,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  FormControlLabel,
  IconButton,
  MenuItem,
  TextField,
  Typography,
} from '@mui/material'
import DeleteIcon from '@mui/icons-material/Delete'
import * as quizService from '../../services/quizService'
import * as subjectService from '../../services/subjectService'
import type { Difficulty, Quiz, QuestionType } from '../../types/quiz'
import type { Subject } from '../../types/subject'

const STATUS_COLOR: Record<string, 'success' | 'warning' | 'default'> = {
  completed: 'success',
  failed: 'warning',
  pending: 'default',
}

const QUESTION_TYPE_LABELS: Record<QuestionType, string> = {
  multiple_choice: 'Multiple choice',
  true_false: 'True/False',
  short_answer: 'Short answer',
}

function QuizzesPage() {
  const navigate = useNavigate()
  const [quizzes, setQuizzes] = useState<Quiz[]>([])
const [subjects, setSubjects] = useState<Subject[]>([])
const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const [isDialogOpen, setIsDialogOpen] = useState(false)
  const [newSubjectId, setNewSubjectId] = useState('')
  const [newDifficulty, setNewDifficulty] = useState<Difficulty>('medium')
  const [newQuestionTypes, setNewQuestionTypes] = useState<QuestionType[]>([
    'multiple_choice',
    'true_false',
    'short_answer',
  ])
  const [newQuestionCount, setNewQuestionCount] = useState(5)
  const [isGenerating, setIsGenerating] = useState(false)
  const [generateError, setGenerateError] = useState<string | null>(null)
  async function loadData() {
    setIsLoading(true)

    try {
      const [quizzesData, subjectsData] = await Promise.all([
        quizService.listQuizzes(),
        subjectService.listSubjects(),
      ])

      setQuizzes(quizzesData)
      setSubjects(subjectsData)
      setError(null)
    } catch {
      setError('Unable to load your quizzes.')
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
    setNewSubjectId('')
    setNewDifficulty('medium')
    setNewQuestionTypes(['multiple_choice', 'true_false', 'short_answer'])
    setNewQuestionCount(5)
    setGenerateError(null)
    setIsDialogOpen(true)
  }

  function toggleQuestionType(type: QuestionType) {
    setNewQuestionTypes((current) =>
      current.includes(type) ? current.filter((value) => value !== type) : [...current, type],
    )
  }

  async function handleGenerate(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    if (newQuestionTypes.length === 0) {
      setGenerateError('Select at least one question type.')
      return
    }
    setGenerateError(null)
    setIsGenerating(true)
    try {
      const quiz = await quizService.createQuiz({
        subject_id: newSubjectId || null,
        difficulty: newDifficulty,
        question_types: newQuestionTypes,
        question_count: newQuestionCount,
      })
      setIsDialogOpen(false)
      navigate(`/quizzes/${quiz.id}`)
    } catch {
      setGenerateError('Unable to generate a quiz right now. Please try again.')
    } finally {
      setIsGenerating(false)
    }
  }

  async function handleDelete(quizId: string) {
    await quizService.deleteQuiz(quizId)
    loadData()
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
            Quizzes
          </Typography>
          <Box sx={{ display: 'flex', gap: 1 }}>
            <Button variant="outlined" component={RouterLink} to="/quizzes/history">
              History
            </Button>
            <Button variant="contained" onClick={openDialog}>
              Generate quiz
            </Button>
          </Box>
        </Box>

        {error && <Alert severity="error">{error}</Alert>}

        {quizzes.length === 0 && !error && (
          <Card>
            <CardContent>
              <Typography variant="body2" color="text.secondary">
                No quizzes yet. Generate one to test yourself on a subject.
              </Typography>
            </CardContent>
          </Card>
        )}

        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
          {quizzes.map((quiz) => (
            <Card key={quiz.id}>
              <CardActionArea component={RouterLink} to={`/quizzes/${quiz.id}`}>
                <CardContent>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 1 }}>
                    <Box>
                      <Typography variant="h6">{quiz.title}</Typography>
                      <Typography variant="body2" color="text.secondary">
                        {subjectName(quiz.subject_id)} · {quiz.question_count} questions
                      </Typography>
                    </Box>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <Chip label={quiz.generation_status} color={STATUS_COLOR[quiz.generation_status] ?? 'default'} size="small" />
                      <IconButton
                        onClick={(event) => {
                          event.preventDefault()
                          event.stopPropagation()
                          handleDelete(quiz.id)
                        }}
                        aria-label="Delete"
                      >
                        <DeleteIcon fontSize="small" />
                      </IconButton>
                    </Box>
                  </Box>
                </CardContent>
              </CardActionArea>
            </Card>
          ))}
        </Box>
      </Box>

      <Dialog open={isDialogOpen} onClose={() => !isGenerating && setIsDialogOpen(false)} fullWidth maxWidth="xs">
        <DialogTitle>Generate a quiz</DialogTitle>
        <Box component="form" onSubmit={handleGenerate}>
          <DialogContent sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
            {generateError && <Alert severity="error">{generateError}</Alert>}
            <TextField
              select
              label="Subject (optional)"
              value={newSubjectId}
              onChange={(event) => setNewSubjectId(event.target.value)}
              fullWidth
              disabled={isGenerating}
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
              label="Difficulty"
              value={newDifficulty}
              onChange={(event) => setNewDifficulty(event.target.value as Difficulty)}
              fullWidth
              disabled={isGenerating}
            >
              <MenuItem value="easy">Easy</MenuItem>
              <MenuItem value="medium">Medium</MenuItem>
              <MenuItem value="hard">Hard</MenuItem>
            </TextField>
            <TextField
              type="number"
              label="Number of questions"
              value={newQuestionCount}
              onChange={(event) => setNewQuestionCount(Number(event.target.value))}
              slotProps={{ htmlInput: { min: 1, max: 10 } }}
              fullWidth
              disabled={isGenerating}
            />
            <Box>
              <Typography variant="body2" gutterBottom>
                Question types
              </Typography>
              {(Object.keys(QUESTION_TYPE_LABELS) as QuestionType[]).map((type) => (
                <FormControlLabel
                  key={type}
                  control={
                    <Checkbox
                      checked={newQuestionTypes.includes(type)}
                      onChange={() => toggleQuestionType(type)}
                      disabled={isGenerating}
                    />
                  }
                  label={QUESTION_TYPE_LABELS[type]}
                />
              ))}
            </Box>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setIsDialogOpen(false)} disabled={isGenerating}>
              Cancel
            </Button>
            <Button type="submit" variant="contained" disabled={isGenerating}>
              {isGenerating ? 'Generating...' : 'Generate'}
            </Button>
          </DialogActions>
        </Box>
      </Dialog>
    </Container>
  )
}

export default QuizzesPage