import { useEffect, useState } from 'react'
import { Link as RouterLink } from 'react-router-dom'
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
import * as dashboardService from '../../services/dashboardService'
import { useAuth } from '../../hooks/useAuth'
import type { DashboardOverview } from '../../types/dashboard'

const FIELD_LABELS: Record<string, string> = {
  full_name: 'Full name',
  academic_level: 'Academic level',
  institution: 'Institution',
  program: 'Program',
  subjects: 'Subjects',
  academic_goals: 'Academic goals',
}

function DashboardPage() {
  const { user } = useAuth()
  const [overview, setOverview] = useState<DashboardOverview | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    dashboardService
      .getOverview()
      .then((data) => setOverview(data))
      .catch(() => setError('Unable to load your dashboard.'))
      .finally(() => setIsLoading(false))
  }, [])

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
        <Box>
          <Typography variant="h4" component="h1" sx={{ fontWeight: 600 }}>
            Welcome back, {user?.email}
          </Typography>
          {overview && (
            <Typography variant="body2" color="text.secondary">
              Member since {new Date(overview.member_since).toLocaleDateString(undefined, {
                year: 'numeric',
                month: 'long',
                day: 'numeric',
              })}
            </Typography>
          )}
        </Box>

        {error && <Alert severity="error">{error}</Alert>}

        {overview && (
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Study Statistics
              </Typography>
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                  <Typography variant="body2">Profile completion</Typography>
                  <Typography variant="body2" sx={{ fontWeight: 600 }}>
                    {overview.profile_completion_percentage}%
                  </Typography>
                </Box>
                <LinearProgress
                  variant="determinate"
                  value={overview.profile_completion_percentage}
                  sx={{ height: 8, borderRadius: 4 }}
                />
                {overview.profile_completion_missing_fields.length > 0 && (
                  <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1, mt: 1 }}>
                    <Typography variant="body2" color="text.secondary">
                      Add these to complete your profile:
                    </Typography>
                    <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                      {overview.profile_completion_missing_fields.map((field) => (
                        <Chip key={field} label={FIELD_LABELS[field] ?? field} size="small" variant="outlined" />
                      ))}
                    </Box>
                    <Button component={RouterLink} to="/profile" size="small" sx={{ alignSelf: 'flex-start' }}>
                      Complete your profile
                    </Button>
                  </Box>
                )}
              </Box>
            </CardContent>
          </Card>
        )}

        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Quick Actions
            </Typography>
            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
              <Button variant="outlined" component={RouterLink} to="/subjects">
                Manage subjects
              </Button>
              <Button variant="outlined" component={RouterLink} to="/profile">
                Edit profile
              </Button>
            </Box>
          </CardContent>
        </Card>

        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Recent Activity
            </Typography>
            <Typography variant="body2" color="text.secondary">
              No recent activity yet. Your study activity will show up here once you start using StudyAssistant AI.
            </Typography>
          </CardContent>
        </Card>

        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Upcoming Sessions
            </Typography>
            <Typography variant="body2" color="text.secondary">
              No study sessions scheduled yet.
            </Typography>
          </CardContent>
        </Card>

        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Weak Areas
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Take a quiz to help identify topics that need more attention.
            </Typography>
          </CardContent>
        </Card>
      </Box>
    </Container>
  )
}

export default DashboardPage