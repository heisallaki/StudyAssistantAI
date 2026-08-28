import { useEffect, useState } from 'react'
import { Link as RouterLink, useNavigate, useParams } from 'react-router-dom'
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
  Divider,
  Typography,
} from '@mui/material'
import * as quizAttemptService from '../../services/quizAttemptService'
import * as quizService from '../../services/quizService'
import type { QuizAttempt } from '../../types/quizAttempt'
import type { QuizDetail, QuizQuestion } from '../../types/quiz'

const STATUS_COLOR: Record<string, 'success' | 'warning' | 'default'> = {
  completed: 'success',
  failed: 'warning',
  pending: 'default',
}

const QUESTION_TYPE_LABELS: Record<string, string> = {
  multiple_choice: 'Multiple choice',
  true_false: 'True / False',
  short_answer: 'Short answer',
}

function QuestionCard({ question, index }: { question: QuizQuestion; index: number }) {
  return (
    <Card>
      <CardContent>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: 1, mb: 1 }}>
          <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>
            {index + 1}. {question.prompt}
          </Typography>
          <Chip label={QUESTION_TYPE_LABELS[question.question_type] ?? question.question_type} size="small" variant="outlined" />
        </Box>

        {question.question_type === 'multiple_choice' && (
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 0.5, mb: 1 }}>
            {question.options.map((option) => (
              <Typography
                key={option}
                variant="body2"
                sx={{
                  fontWeight: option === question.correct_answer ? 600 : 400,
                  color: option === question.correct_answer ? 'success.main' : 'text.primary',
                }}
              >
                {option === question.correct_answer ? '✓ ' : '• '}
                {option}
              </Typography>
            ))}
          </Box>
        )}

        {question.question_type === 'true_false' && (
          <Typography variant="body2" sx={{ fontWeight: 600, color: 'success.main', mb: 1 }}>
            Correct answer: {question.correct_answer === 'true' ? 'True' : 'False'}
          </Typography>
        )}

        {question.question_type === 'short_answer' && (
          <Typography variant="body2" sx={{ fontWeight: 600, color: 'success.main', mb: 1 }}>
            Expected answer: {question.correct_answer}
          </Typography>
        )}

        {question.explanation && (
          <>
            <Divider sx={{ my: 1 }} />
            <Typography variant="body2" color="text.secondary">
              {question.explanation}
            </Typography>
          </>
        )}
      </CardContent>
    </Card>
  )
}

function QuizDetailPage() {
  const { quizId } = useParams<{ quizId: string }>()
  const navigate = useNavigate()

  const [quiz, setQuiz] = useState<QuizDetail | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false)
  const [isDeleting, setIsDeleting] = useState(false)
  const [attempts, setAttempts] = useState<QuizAttempt[]>([])
  const [isStarting, setIsStarting] = useState(false)
  const [startError, setStartError] = useState<string | null>(null)

  useEffect(() => {
    if (!quizId) return
    quizService
      .getQuiz(quizId)
      .then((data) => setQuiz(data))
      .catch(() => setError('Unable to load this quiz.'))
      .finally(() => setIsLoading(false))
  }, [quizId])

  useEffect(() => {
    if (!quizId) return
    quizAttemptService
      .listAttempts({ quiz_id: quizId })
      .then(setAttempts)
      .catch(() => setAttempts([]))
  }, [quizId])

  async function handleDelete() {
    if (!quizId) return
    setIsDeleting(true)
    try {
      await quizService.deleteQuiz(quizId)
      navigate('/quizzes')
    } finally {
      setIsDeleting(false)
    }
  }

  async function handleStartAttempt() {
    if (!quizId) return
    setIsStarting(true)
    setStartError(null)
    try {
      const attempt = await quizAttemptService.startAttempt(quizId)
      navigate(`/quizzes/${quizId}/attempts/${attempt.id}`)
    } catch {
      setStartError('Unable to start this quiz right now.')
    } finally {
      setIsStarting(false)
    }
  }

  if (isLoading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '60vh' }}>
        <CircularProgress />
      </Box>
    )
  }

  if (error || !quiz) {
    return (
      <Container maxWidth="sm">
        <Alert severity="error" sx={{ mt: 4 }}>
          {error ?? 'Quiz not found.'}
        </Alert>
      </Container>
    )
  }

  const canAttempt = quiz.generation_status === 'completed' && quiz.questions.length > 0

  return (
    <Container maxWidth="md">
      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3, py: 4 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: 2, flexWrap: 'wrap' }}>
          <Box>
            <Typography variant="h4" component="h1" sx={{ fontWeight: 600 }}>
              {quiz.title}
            </Typography>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mt: 1 }}>
              <Chip label={quiz.generation_status} color={STATUS_COLOR[quiz.generation_status] ?? 'default'} size="small" />
              <Typography variant="body2" color="text.secondary">
                {quiz.question_count} questions · {quiz.difficulty}
              </Typography>
            </Box>
          </Box>
          <Box sx={{ display: 'flex', gap: 1 }}>
            <Button variant="contained" onClick={handleStartAttempt} disabled={!canAttempt || isStarting}>
              {isStarting ? 'Starting...' : 'Start quiz'}
            </Button>
            <Button variant="outlined" color="error" onClick={() => setIsDeleteDialogOpen(true)}>
              Delete
            </Button>
          </Box>
        </Box>

        {startError && <Alert severity="error">{startError}</Alert>}

        {quiz.generation_status === 'failed' && (
          <Alert severity="warning">
            {quiz.generation_error ?? 'Quiz generation failed.'} Delete this quiz and try generating again.
          </Alert>
        )}

        {attempts.length > 0 && (
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>
                  Your attempts
                </Typography>
                <Button component={RouterLink} to="/quizzes/history" size="small">
                  View all history
                </Button>
              </Box>
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                {attempts.slice(0, 5).map((attempt) => (
                  <CardActionArea
                    key={attempt.id}
                    component={RouterLink}
                    to={`/quizzes/${quiz.id}/attempts/${attempt.id}`}
                    sx={{ borderRadius: 1, p: 1 }}
                  >
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <Typography variant="body2" color="text.secondary">
                        {new Date(attempt.started_at).toLocaleString()}
                      </Typography>
                      {attempt.status === 'completed' ? (
                        <Chip
                          label={`${attempt.score} / ${attempt.total_questions}`}
                          color={(attempt.percentage_score ?? 0) >= 70 ? 'success' : 'default'}
                          size="small"
                        />
                      ) : (
                        <Chip label="In progress" color="warning" size="small" />
                      )}
                    </Box>
                  </CardActionArea>
                ))}
              </Box>
            </CardContent>
          </Card>
        )}

        {quiz.questions.map((question, index) => (
          <QuestionCard key={question.id} question={question} index={index} />
        ))}
      </Box>

      <Dialog open={isDeleteDialogOpen} onClose={() => setIsDeleteDialogOpen(false)}>
        <DialogTitle>Delete "{quiz.title}"?</DialogTitle>
        <DialogContent>
          <Typography variant="body2">This will permanently delete this quiz.</Typography>
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

export default QuizDetailPage