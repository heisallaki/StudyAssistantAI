import { useEffect, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
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
  Typography,
} from '@mui/material'
import * as quizService from '../../services/quizService'
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

  useEffect(() => {
    if (!quizId) return
    quizService
      .getQuiz(quizId)
      .then((data) => setQuiz(data))
      .catch(() => setError('Unable to load this quiz.'))
      .finally(() => setIsLoading(false))
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
          <Button variant="outlined" color="error" onClick={() => setIsDeleteDialogOpen(true)}>
            Delete
          </Button>
        </Box>

        {quiz.generation_status === 'failed' && (
          <Alert severity="warning">
            {quiz.generation_error ?? 'Quiz generation failed.'} Delete this quiz and try generating again.
          </Alert>
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