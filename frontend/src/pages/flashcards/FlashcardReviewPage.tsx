import { useEffect, useState } from 'react'
import { Link as RouterLink, useParams } from 'react-router-dom'
import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  Chip,
  CircularProgress,
  Container,
  LinearProgress,
  Typography,
} from '@mui/material'
import * as flashcardService from '../../services/flashcardService'
import type { Flashcard, MasteryStatus, ReviewResult } from '../../types/flashcard'

const STATUS_LABEL: Record<MasteryStatus, string> = {
  new: 'New',
  learning: 'Learning',
  mastered: 'Mastered',
}

function FlashcardReviewPage() {
  const { deckId } = useParams<{ deckId: string }>()

  const [queue, setQueue] = useState<Flashcard[]>([])
  const [currentIndex, setCurrentIndex] = useState(0)
  const [isRevealed, setIsRevealed] = useState(false)
  const [isLoading, setIsLoading] = useState(true)
  const [loadError, setLoadError] = useState<string | null>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [reviewedCount, setReviewedCount] = useState(0)
  const [masteredCount, setMasteredCount] = useState(0)

  useEffect(() => {
    if (!deckId) return
    flashcardService
      .getReviewQueue(deckId)
      .then((data) => setQueue(data))
      .catch(() => setLoadError('Unable to load cards to review.'))
      .finally(() => setIsLoading(false))
  }, [deckId])

  async function handleAnswer(result: ReviewResult) {
    if (!deckId) return
    const current = queue[currentIndex]
    if (!current) return
    setIsSubmitting(true)
    try {
      const updated = await flashcardService.reviewFlashcard(deckId, current.id, { result })
      setReviewedCount((count) => count + 1)
      if (updated.progress.status === 'mastered') {
        setMasteredCount((count) => count + 1)
      }
      setIsRevealed(false)
      setCurrentIndex((index) => index + 1)
    } finally {
      setIsSubmitting(false)
    }
  }

  if (isLoading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '60vh' }}>
        <CircularProgress />
      </Box>
    )
  }

  if (loadError) {
    return (
      <Container maxWidth="sm">
        <Alert severity="error" sx={{ mt: 4 }}>
          {loadError}
        </Alert>
      </Container>
    )
  }

  if (queue.length === 0) {
    return (
      <Container maxWidth="sm">
        <Box
          sx={{
            display: 'flex',
            flexDirection: 'column',
            gap: 2,
            py: 6,
            alignItems: 'center',
            textAlign: 'center',
          }}
        >
          <Typography variant="h5" sx={{ fontWeight: 600 }}>
            Nothing to review right now
          </Typography>
          <Typography variant="body2" color="text.secondary">
            All your cards in this deck are mastered, or the deck has no cards yet.
          </Typography>
          <Button variant="contained" component={RouterLink} to={`/flashcards/${deckId}`}>
            Back to deck
          </Button>
        </Box>
      </Container>
    )
  }

  if (currentIndex >= queue.length) {
    return (
      <Container maxWidth="sm">
        <Box
          sx={{
            display: 'flex',
            flexDirection: 'column',
            gap: 2,
            py: 6,
            alignItems: 'center',
            textAlign: 'center',
          }}
        >
          <Typography variant="h5" sx={{ fontWeight: 600 }}>
            Review complete
          </Typography>
          <Typography variant="body2" color="text.secondary">
            You reviewed {reviewedCount} card{reviewedCount === 1 ? '' : 's'}, {masteredCount} newly mastered.
          </Typography>
          <Button variant="contained" component={RouterLink} to={`/flashcards/${deckId}`}>
            Back to deck
          </Button>
        </Box>
      </Container>
    )
  }

  const current = queue[currentIndex]

  return (
    <Container maxWidth="sm">
      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3, py: 4 }}>
        <Box>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
            Card {currentIndex + 1} of {queue.length}
          </Typography>
          <LinearProgress
            variant="determinate"
            value={(currentIndex / queue.length) * 100}
            sx={{ height: 6, borderRadius: 3 }}
          />
        </Box>

        <Card sx={{ minHeight: 220 }}>
          <CardContent
            sx={{
              display: 'flex',
              flexDirection: 'column',
              justifyContent: 'center',
              alignItems: 'center',
              minHeight: 220,
              textAlign: 'center',
              gap: 2,
            }}
          >
            <Chip label={STATUS_LABEL[current.progress.status]} size="small" />
            <Typography variant="h6">{current.front}</Typography>
            {isRevealed && (
              <>
                <Box sx={{ width: '100%', borderTop: 1, borderColor: 'divider', my: 1 }} />
                <Typography variant="body1" color="text.secondary">
                  {current.back}
                </Typography>
              </>
            )}
          </CardContent>
        </Card>

        {isRevealed ? (
          <Box sx={{ display: 'flex', gap: 2 }}>
            <Button
              fullWidth
              variant="outlined"
              color="error"
              onClick={() => handleAnswer('again')}
              disabled={isSubmitting}
            >
              Again
            </Button>
            <Button
              fullWidth
              variant="contained"
              color="success"
              onClick={() => handleAnswer('good')}
              disabled={isSubmitting}
            >
              Good
            </Button>
          </Box>
        ) : (
          <Button variant="contained" size="large" onClick={() => setIsRevealed(true)}>
            Show answer
          </Button>
        )}
      </Box>
    </Container>
  )
}

export default FlashcardReviewPage