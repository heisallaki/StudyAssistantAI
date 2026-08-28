import { useEffect, useState } from 'react'
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
  Divider,
  FormControlLabel,
  LinearProgress,
  Radio,
  RadioGroup,
  TextField,
  Typography,
} from '@mui/material'
import CancelIcon from '@mui/icons-material/Cancel'
import CheckCircleIcon from '@mui/icons-material/CheckCircle'
import * as quizAttemptService from '../../services/quizAttemptService'
import type { QuizAttemptDetail, QuizAttemptQuestionResult } from '../../types/quizAttempt'

const QUESTION_TYPE_LABELS: Record<string, string> = {
  multiple_choice: 'Multiple choice',
  true_false: 'True / False',
  short_answer: 'Short answer',
}

interface QuestionInputCardProps {
  question: QuizAttemptQuestionResult
  index: number
  value: string
  isSaving: boolean
  error: string | null
  onChange: (value: string) => void
  onCommit: (value: string) => void
}

function QuestionInputCard({
  question,
  index,
  value,
  isSaving,
  error,
  onChange,
  onCommit,
}: QuestionInputCardProps) {
  return (
    <Card>
      <CardContent>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: 1, mb: 2 }}>
          <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>
            {index + 1}. {question.prompt}
          </Typography>
          <Chip
            label={QUESTION_TYPE_LABELS[question.question_type] ?? question.question_type}
            size="small"
            variant="outlined"
          />
        </Box>

        {question.question_type === 'multiple_choice' && (
          <RadioGroup
            value={value}
            onChange={(event) => {
              onChange(event.target.value)
              onCommit(event.target.value)
            }}
          >
            {question.options.map((option) => (
              <FormControlLabel
                key={option}
                value={option}
                control={<Radio disabled={isSaving} />}
                label={option}
              />
            ))}
          </RadioGroup>
        )}

        {question.question_type === 'true_false' && (
          <RadioGroup
            value={value}
            onChange={(event) => {
              onChange(event.target.value)
              onCommit(event.target.value)
            }}
          >
            <FormControlLabel value="true" control={<Radio disabled={isSaving} />} label="True" />
            <FormControlLabel value="false" control={<Radio disabled={isSaving} />} label="False" />
          </RadioGroup>
        )}

        {question.question_type === 'short_answer' && (
          <TextField
            value={value}
            onChange={(event) => onChange(event.target.value)}
            onBlur={(event) => onCommit(event.target.value)}
            disabled={isSaving}
            fullWidth
            placeholder="Type your answer"
          />
        )}

        {error && (
          <Alert severity="error" sx={{ mt: 1 }}>
            {error}
          </Alert>
        )}
      </CardContent>
    </Card>
  )
}

function QuestionResultCard({ question, index }: { question: QuizAttemptQuestionResult; index: number }) {
  return (
    <Card>
      <CardContent>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: 1, mb: 1 }}>
          <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>
            {index + 1}. {question.prompt}
          </Typography>
          {question.is_correct ? (
            <CheckCircleIcon color="success" fontSize="small" />
          ) : (
            <CancelIcon color="error" fontSize="small" />
          )}
        </Box>

        {question.question_type === 'multiple_choice' && (
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 0.5, mb: 1 }}>
            {question.options.map((option) => {
              const isSubmitted = option === question.submitted_answer
              const isCorrectOption = option === question.correct_answer
              return (
                <Typography
                  key={option}
                  variant="body2"
                  sx={{
                    fontWeight: isCorrectOption ? 600 : 400,
                    color: isCorrectOption ? 'success.main' : isSubmitted ? 'error.main' : 'text.primary',
                  }}
                >
                  {isCorrectOption ? '✓ ' : isSubmitted ? '✗ ' : '• '}
                  {option}
                </Typography>
              )
            })}
          </Box>
        )}

        {question.question_type !== 'multiple_choice' && (
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 0.5, mb: 1 }}>
            <Typography variant="body2">
              Your answer: {question.submitted_answer ? question.submitted_answer : '(no answer submitted)'}
            </Typography>
            {!question.is_correct && (
              <Typography variant="body2" sx={{ fontWeight: 600, color: 'success.main' }}>
                Correct answer:{' '}
                {question.question_type === 'true_false'
                  ? question.correct_answer === 'true'
                    ? 'True'
                    : 'False'
                  : question.correct_answer}
              </Typography>
            )}
          </Box>
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

function QuizAttemptPage() {
  const { quizId, attemptId } = useParams<{ quizId: string; attemptId: string }>()
  const navigate = useNavigate()

  const [attempt, setAttempt] = useState<QuizAttemptDetail | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [loadError, setLoadError] = useState<string | null>(null)
  const [answers, setAnswers] = useState<Record<string, string>>({})
  const [savingQuestionId, setSavingQuestionId] = useState<string | null>(null)
  const [answerErrors, setAnswerErrors] = useState<Record<string, string>>({})
  const [isCompleting, setIsCompleting] = useState(false)
  const [completeError, setCompleteError] = useState<string | null>(null)
  const [isRetaking, setIsRetaking] = useState(false)

  useEffect(() => {
    if (!attemptId) return
    quizAttemptService
      .getAttempt(attemptId)
      .then((data) => {
        setAttempt(data)
        const initialAnswers: Record<string, string> = {}
        data.answers.forEach((question) => {
          initialAnswers[question.question_id] = question.submitted_answer ?? ''
        })
        setAnswers(initialAnswers)
      })
      .catch(() => setLoadError('Unable to load this quiz attempt.'))
      .finally(() => setIsLoading(false))
  }, [attemptId])

  function handleAnswerChange(questionId: string, value: string) {
    setAnswers((current) => ({ ...current, [questionId]: value }))
  }

  async function handleAnswerCommit(questionId: string, value: string) {
    if (!attemptId) return
    setSavingQuestionId(questionId)
    try {
      await quizAttemptService.submitAnswer(attemptId, questionId, { submitted_answer: value })
      setAnswerErrors((current) => {
        const next = { ...current }
        delete next[questionId]
        return next
      })
    } catch {
      setAnswerErrors((current) => ({
        ...current,
        [questionId]: 'Unable to save this answer. Please try again.',
      }))
    } finally {
      setSavingQuestionId(null)
    }
  }

  async function handleFinishQuiz() {
    if (!attemptId) return
    setIsCompleting(true)
    setCompleteError(null)
    try {
      const result = await quizAttemptService.completeAttempt(attemptId)
      setAttempt(result)
    } catch {
      setCompleteError('Unable to submit your quiz right now. Please try again.')
    } finally {
      setIsCompleting(false)
    }
  }

  async function handleRetake() {
    if (!quizId) return
    setIsRetaking(true)
    try {
      const newAttempt = await quizAttemptService.startAttempt(quizId)
      navigate(`/quizzes/${quizId}/attempts/${newAttempt.id}`)
    } finally {
      setIsRetaking(false)
    }
  }

  if (isLoading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '60vh' }}>
        <CircularProgress />
      </Box>
    )
  }

  if (loadError || !attempt) {
    return (
      <Container maxWidth="sm">
        <Alert severity="error" sx={{ mt: 4 }}>
          {loadError ?? 'Quiz attempt not found.'}
        </Alert>
      </Container>
    )
  }

  const answeredCount = attempt.answers.filter(
    (question) => (answers[question.question_id] ?? '').trim() !== '',
  ).length

  if (attempt.status === 'in_progress') {
    return (
      <Container maxWidth="md">
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3, py: 4 }}>
          <Box>
            <Typography variant="h4" component="h1" sx={{ fontWeight: 600 }}>
              {attempt.quiz_title}
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
              {answeredCount} of {attempt.total_questions} answered
            </Typography>
            <LinearProgress
              variant="determinate"
              value={(answeredCount / attempt.total_questions) * 100}
              sx={{ mt: 1, borderRadius: 1 }}
            />
          </Box>

          {attempt.answers.map((question, index) => (
            <QuestionInputCard
              key={question.question_id}
              question={question}
              index={index}
              value={answers[question.question_id] ?? ''}
              isSaving={savingQuestionId === question.question_id}
              error={answerErrors[question.question_id] ?? null}
              onChange={(value) => handleAnswerChange(question.question_id, value)}
              onCommit={(value) => handleAnswerCommit(question.question_id, value)}
            />
          ))}

          {completeError && <Alert severity="error">{completeError}</Alert>}

          <Box sx={{ display: 'flex', justifyContent: 'flex-end' }}>
            <Button variant="contained" size="large" onClick={handleFinishQuiz} disabled={isCompleting}>
              {isCompleting ? 'Submitting...' : 'Finish quiz'}
            </Button>
          </Box>
        </Box>
      </Container>
    )
  }

  return (
    <Container maxWidth="md">
      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3, py: 4 }}>
        <Card>
          <CardContent>
            <Typography variant="h4" component="h1" sx={{ fontWeight: 600 }}>
              {attempt.quiz_title}
            </Typography>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mt: 2, flexWrap: 'wrap' }}>
              <Chip
                label={`${attempt.score ?? 0} / ${attempt.total_questions} correct`}
                color={(attempt.percentage_score ?? 0) >= 70 ? 'success' : 'default'}
                size="medium"
              />
              <Typography variant="h6">{attempt.percentage_score ?? 0}%</Typography>
            </Box>
          </CardContent>
        </Card>

        {attempt.answers.map((question, index) => (
          <QuestionResultCard key={question.question_id} question={question} index={index} />
        ))}

        <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
          <Button variant="contained" onClick={handleRetake} disabled={isRetaking}>
            {isRetaking ? 'Starting...' : 'Retake quiz'}
          </Button>
          <Button variant="outlined" component={RouterLink} to={`/quizzes/${quizId}`}>
            Back to quiz
          </Button>
          <Button variant="outlined" component={RouterLink} to="/quizzes/history">
            View history
          </Button>
        </Box>
      </Box>
    </Container>
  )
}

export default QuizAttemptPage