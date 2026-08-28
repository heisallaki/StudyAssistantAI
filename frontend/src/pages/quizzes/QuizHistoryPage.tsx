import { useEffect, useState } from 'react'
import { Link as RouterLink } from 'react-router-dom'
import {
  Alert,
  Box,
  Card,
  CardActionArea,
  CardContent,
  Chip,
  CircularProgress,
  Container,
  MenuItem,
  TextField,
  Typography,
} from '@mui/material'
import * as quizAttemptService from '../../services/quizAttemptService'
import * as subjectService from '../../services/subjectService'
import type { QuizAttempt } from '../../types/quizAttempt'
import type { Subject } from '../../types/subject'

function formatDate(value: string): string {
  return new Date(value).toLocaleString()
}

function QuizHistoryPage() {
  const [attempts, setAttempts] = useState<QuizAttempt[]>([])
  const [subjects, setSubjects] = useState<Subject[]>([])
  const [subjectFilter, setSubjectFilter] = useState('')
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  async function loadAttempts(subjectId: string) {
    setIsLoading(true)
    try {
      const data = await quizAttemptService.listAttempts(subjectId ? { subject_id: subjectId } : {})
      setAttempts(data)
      setError(null)
    } catch {
      setError('Unable to load your quiz history.')
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    const timeoutId = window.setTimeout(() => {
      subjectService
        .listSubjects()
        .then(setSubjects)
        .catch(() => setSubjects([]))
      void loadAttempts('')
    }, 0)

    return () => window.clearTimeout(timeoutId)
  }, [])

  function handleSubjectChange(value: string) {
    setSubjectFilter(value)
    loadAttempts(value)
  }

  function subjectName(subjectId: string | null): string {
    if (!subjectId) return 'General'
    return subjects.find((subject) => subject.id === subjectId)?.name ?? 'Unknown subject'
  }

  return (
    <Container maxWidth="md">
      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3, py: 4 }}>
        <Box
          sx={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            flexWrap: 'wrap',
            gap: 2,
          }}
        >
          <Typography variant="h4" component="h1" sx={{ fontWeight: 600 }}>
            Quiz history
          </Typography>
          <TextField
            select
            label="Subject"
            value={subjectFilter}
            onChange={(event) => handleSubjectChange(event.target.value)}
            sx={{ minWidth: 220 }}
          >
            <MenuItem value="">All subjects</MenuItem>
            {subjects.map((subject) => (
              <MenuItem key={subject.id} value={subject.id}>
                {subject.name}
              </MenuItem>
            ))}
          </TextField>
        </Box>

        {error && <Alert severity="error">{error}</Alert>}

        {isLoading ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', py: 6 }}>
            <CircularProgress />
          </Box>
        ) : attempts.length === 0 ? (
          <Card>
            <CardContent>
              <Typography variant="body2" color="text.secondary">
                No quiz attempts yet. Take a quiz to see your history here.
              </Typography>
            </CardContent>
          </Card>
        ) : (
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
            {attempts.map((attempt) => (
              <Card key={attempt.id}>
                <CardActionArea
                  component={RouterLink}
                  to={`/quizzes/${attempt.quiz_id}/attempts/${attempt.id}`}
                >
                  <CardContent>
                    <Box
                      sx={{
                        display: 'flex',
                        justifyContent: 'space-between',
                        alignItems: 'center',
                        flexWrap: 'wrap',
                        gap: 1,
                      }}
                    >
                      <Box>
                        <Typography variant="h6">{attempt.quiz_title}</Typography>
                        <Typography variant="body2" color="text.secondary">
                          {subjectName(attempt.subject_id)} · {formatDate(attempt.started_at)}
                        </Typography>
                      </Box>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        {attempt.status === 'completed' ? (
                          <Chip
                            label={`${attempt.score} / ${attempt.total_questions} (${attempt.percentage_score}%)`}
                            color={(attempt.percentage_score ?? 0) >= 70 ? 'success' : 'default'}
                            size="small"
                          />
                        ) : (
                          <Chip label="In progress" color="warning" size="small" />
                        )}
                      </Box>
                    </Box>
                  </CardContent>
                </CardActionArea>
              </Card>
            ))}
          </Box>
        )}
      </Box>
    </Container>
  )
}

export default QuizHistoryPage