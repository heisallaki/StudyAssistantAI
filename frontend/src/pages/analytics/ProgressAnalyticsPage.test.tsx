import { render, screen } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'
import ProgressAnalyticsPage from './ProgressAnalyticsPage'
import * as analyticsService from '../../services/analyticsService'
import type { AnalyticsOverview } from '../../types/analytics'

vi.mock('../../services/analyticsService')

const mockedAnalyticsService = vi.mocked(analyticsService)

const baseOverview: AnalyticsOverview = {
  total_study_minutes: 125,
  total_quizzes_taken: 7,
  average_quiz_score: 82,
  total_flashcards_reviewed: 9,
  flashcards_mastered: 0,
  total_flashcards: 1,
  subjects_count: 3,
  active_goals_count: 4,
}

function mockOverview(overview: AnalyticsOverview) {
  mockedAnalyticsService.getOverview.mockResolvedValue(overview)
  mockedAnalyticsService.getPerformanceTrend.mockResolvedValue([])
  mockedAnalyticsService.getStudyTime.mockResolvedValue([])
  mockedAnalyticsService.getSubjectBreakdown.mockResolvedValue([])
  mockedAnalyticsService.getWeakAreas.mockResolvedValue([])
}

describe('ProgressAnalyticsPage', () => {
  it('shows the total flashcard count separately from the mastered count', async () => {
    mockOverview(baseOverview)

    render(<ProgressAnalyticsPage />)

    expect(await screen.findByText('Total flashcards')).toBeInTheDocument()
    expect(screen.getByText('1')).toBeInTheDocument()
    expect(screen.getByText('Flashcards mastered')).toBeInTheDocument()
    expect(screen.getByText('0')).toBeInTheDocument()
    expect(screen.queryByText('No flashcards yet')).not.toBeInTheDocument()
  })

  it('shows a mastery percentage once at least one flashcard exists', async () => {
    mockOverview({ ...baseOverview, total_flashcards: 4, flashcards_mastered: 1 })

    render(<ProgressAnalyticsPage />)

    expect(await screen.findByText('4')).toBeInTheDocument()
    expect(screen.getByText('25% of 4')).toBeInTheDocument()
  })

  it('shows a friendly message instead of a percentage when there are no flashcards', async () => {
    mockOverview({ ...baseOverview, total_flashcards: 0, flashcards_mastered: 0 })

    render(<ProgressAnalyticsPage />)

    expect(await screen.findByText('No flashcards yet')).toBeInTheDocument()
  })
})