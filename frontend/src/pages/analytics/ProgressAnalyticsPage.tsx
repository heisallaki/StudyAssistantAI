import { useCallback, useEffect, useState } from 'react'
import { Alert, Box, Card, CardContent, CircularProgress, Container, MenuItem, TextField, Typography } from '@mui/material'
import {
  Bar,
  BarChart,
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
import * as analyticsService from '../../services/analyticsService'
import type {
  AnalyticsOverview,
  PerformanceTrendPoint,
  StudyTimePoint,
  SubjectBreakdown,
  WeakArea,
} from '../../types/analytics'

function formatMinutes(minutes: number): string {
  const hours = Math.floor(minutes / 60)
  const remaining = minutes % 60
  if (hours === 0) return `${remaining}m`
  return `${hours}h ${remaining}m`
}

function formatShortDate(value: string): string {
  const [year, month, day] = value.split('-').map(Number)
  return new Date(year, month - 1, day).toLocaleDateString(undefined, { month: 'short', day: 'numeric' })
}

const WEAK_AREA_REASON_LABEL: Record<string, string> = {
  low_quiz_scores: 'Low quiz scores',
  low_topic_progress: 'Low topic progress',
}

interface StatCardProps {
  label: string
  value: string
  secondary?: string
}

function StatCard({ label, value, secondary }: StatCardProps) {
  return (
    <Card>
      <CardContent>
        <Typography variant="body2" color="text.secondary">
          {label}
        </Typography>
        <Typography variant="h5" sx={{ fontWeight: 600, mt: 0.5 }}>
          {value}
        </Typography>
        {secondary && (
          <Typography variant="caption" color="text.secondary">
            {secondary}
          </Typography>
        )}
      </CardContent>
    </Card>
  )
}

function ProgressAnalyticsPage() {
  const [overview, setOverview] = useState<AnalyticsOverview | null>(null)
  const [trend, setTrend] = useState<PerformanceTrendPoint[]>([])
  const [studyTime, setStudyTime] = useState<StudyTimePoint[]>([])
  const [breakdown, setBreakdown] = useState<SubjectBreakdown[]>([])
  const [weakAreas, setWeakAreas] = useState<WeakArea[]>([])
  const [days, setDays] = useState(30)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const loadData = useCallback(async () => {
    setIsLoading(true)
    try {
      const [overviewData, trendData, studyTimeData, breakdownData, weakAreasData] = await Promise.all([
        analyticsService.getOverview(),
        analyticsService.getPerformanceTrend(days),
        analyticsService.getStudyTime(days),
        analyticsService.getSubjectBreakdown(),
        analyticsService.getWeakAreas(),
      ])
      setOverview(overviewData)
      setTrend(trendData)
      setStudyTime(studyTimeData)
      setBreakdown(breakdownData)
      setWeakAreas(weakAreasData)
      setError(null)
    } catch {
      setError('Unable to load your progress analytics.')
    } finally {
      setIsLoading(false)
    }
  }, [days])

  useEffect(() => {
    const timeoutId = window.setTimeout(() => {
      void loadData()
    }, 0)
    return () => window.clearTimeout(timeoutId)
  }, [loadData])

  if (isLoading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '60vh' }}>
        <CircularProgress />
      </Box>
    )
  }

  if (error || !overview) {
    return (
      <Container maxWidth="md">
        <Alert severity="error" sx={{ mt: 4 }}>
          {error ?? 'Unable to load analytics.'}
        </Alert>
      </Container>
    )
  }

  const trendChartData = trend.map((point) => ({ ...point, label: formatShortDate(point.date) }))
  const studyTimeChartData = studyTime.map((point) => ({ ...point, label: formatShortDate(point.date) }))
  const breakdownChartData = breakdown.map((subject) => ({
    name: subject.name,
    'Topic progress': subject.topic_progress_percentage,
    'Quiz average': subject.quiz_average_score ?? 0,
    'Flashcard mastery': subject.flashcard_mastery_percentage ?? 0,
  }))

  return (
    <Container maxWidth="md">
      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3, py: 4 }}>
        <Box
          sx={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            flexWrap: 'wrap',
            gap: 1,
          }}
        >
          <Typography variant="h4" component="h1" sx={{ fontWeight: 600 }}>
            Progress Analytics
          </Typography>
          <TextField
            select
            label="Range"
            value={days}
            onChange={(event) => setDays(Number(event.target.value))}
            size="small"
            sx={{ minWidth: 160 }}
          >
            <MenuItem value={7}>Last 7 days</MenuItem>
            <MenuItem value={30}>Last 30 days</MenuItem>
            <MenuItem value={90}>Last 90 days</MenuItem>
          </TextField>
        </Box>

        <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr 1fr', sm: 'repeat(4, 1fr)' }, gap: 2 }}>
          <StatCard label="Study time" value={formatMinutes(overview.total_study_minutes)} />
          <StatCard
            label="Quizzes taken"
            value={String(overview.total_quizzes_taken)}
            secondary={
              overview.average_quiz_score !== null ? `${overview.average_quiz_score}% average` : undefined
            }
          />
          <StatCard
            label="Flashcards mastered"
            value={`${overview.flashcards_mastered}/${overview.total_flashcards}`}
          />
          <StatCard
            label="Subjects"
            value={String(overview.subjects_count)}
            secondary={`${overview.active_goals_count} active goal(s)`}
          />
        </Box>

        {weakAreas.length > 0 && (
          <Card>
            <CardContent>
              <Typography variant="subtitle1" sx={{ fontWeight: 600, mb: 1 }}>
                Areas that need attention
              </Typography>
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                {weakAreas.map((area, index) => (
                  <Alert key={index} severity="warning">
                    <strong>{area.name}</strong> — {WEAK_AREA_REASON_LABEL[area.reason] ?? area.reason} (
                    {area.metric_value}%)
                  </Alert>
                ))}
              </Box>
            </CardContent>
          </Card>
        )}

        <Card>
          <CardContent>
            <Typography variant="subtitle1" sx={{ fontWeight: 600, mb: 2 }}>
              Quiz performance trend
            </Typography>
            {trendChartData.length === 0 ? (
              <Typography variant="body2" color="text.secondary">
                No completed quizzes in this range yet.
              </Typography>
            ) : (
              <ResponsiveContainer width="100%" height={260}>
                <LineChart data={trendChartData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="label" />
                  <YAxis domain={[0, 100]} />
                  <Tooltip />
                  <Line
                    type="monotone"
                    dataKey="average_score"
                    name="Average score (%)"
                    stroke="#1976d2"
                    strokeWidth={2}
                  />
                </LineChart>
              </ResponsiveContainer>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardContent>
            <Typography variant="subtitle1" sx={{ fontWeight: 600, mb: 2 }}>
              Study time
            </Typography>
            <ResponsiveContainer width="100%" height={260}>
              <BarChart data={studyTimeChartData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="label" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="minutes" name="Minutes studied" fill="#2e7d32" />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        <Card>
          <CardContent>
            <Typography variant="subtitle1" sx={{ fontWeight: 600, mb: 2 }}>
              Subject breakdown
            </Typography>
            {breakdownChartData.length === 0 ? (
              <Typography variant="body2" color="text.secondary">
                Add a subject to see a breakdown here.
              </Typography>
            ) : (
              <>
                <ResponsiveContainer width="100%" height={Math.max(260, breakdownChartData.length * 70)}>
                  <BarChart data={breakdownChartData} layout="vertical" margin={{ left: 24 }}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis type="number" domain={[0, 100]} />
                    <YAxis type="category" dataKey="name" width={100} />
                    <Tooltip />
                    <Legend />
                    <Bar dataKey="Topic progress" fill="#1976d2" />
                    <Bar dataKey="Quiz average" fill="#9c27b0" />
                    <Bar dataKey="Flashcard mastery" fill="#2e7d32" />
                  </BarChart>
                </ResponsiveContainer>
                <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mt: 1 }}>
                  Quiz average and flashcard mastery show as 0% for subjects with no attempts or cards yet.
                </Typography>
              </>
            )}
          </CardContent>
        </Card>
      </Box>
    </Container>
  )
}

export default ProgressAnalyticsPage