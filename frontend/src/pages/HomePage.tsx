import { useEffect, useState } from 'react'
import { Link as RouterLink } from 'react-router-dom'
import { Box, Button, Card, CardContent, Chip, CircularProgress, Container, Typography } from '@mui/material'
import apiClient from '../services/api'
import { useAuth } from '../hooks/useAuth'
import type { HealthStatus } from '../types/health'

function HomePage() {
  const { user, logout } = useAuth()
  const [health, setHealth] = useState<HealthStatus | null>(null)
  const [healthError, setHealthError] = useState<string | null>(null)
  const [isLoadingHealth, setIsLoadingHealth] = useState(true)

  useEffect(() => {
    let isMounted = true

    apiClient
      .get<HealthStatus>('/health')
      .then((response) => {
        if (isMounted) {
          setHealth(response.data)
          setIsLoadingHealth(false)
        }
      })
      .catch(() => {
        if (isMounted) {
          setHealthError('Unable to reach the backend API')
          setIsLoadingHealth(false)
        }
      })

    return () => {
      isMounted = false
    }
  }, [])

  return (
    <Container maxWidth="sm">
      <Box
        sx={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          minHeight: '100vh',
          gap: 3,
        }}
      >
        <Typography variant="h4" component="h1" sx={{ fontWeight: 600 }}>
          StudyAssistant AI
        </Typography>
        <Card sx={{ width: '100%' }}>
          <CardContent>
            <Typography variant="subtitle1" gutterBottom>
              Welcome, {user?.email}
            </Typography>
            <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
              <Button variant="outlined" color="secondary" onClick={logout}>
                Log out
              </Button>
              <Button variant="outlined" component={RouterLink} to="/profile">
                Edit profile
              </Button>
            </Box>
            <Typography variant="subtitle2" gutterBottom>
              System Status
            </Typography>
            {isLoadingHealth && <CircularProgress size={24} />}
            {!isLoadingHealth && healthError && <Chip label={healthError} color="error" />}
            {!isLoadingHealth && health && (
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <Typography variant="body2">API:</Typography>
                  <Chip label={health.status} color={health.status === 'ok' ? 'success' : 'warning'} size="small" />
                </Box>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <Typography variant="body2">Database:</Typography>
                  <Chip
                    label={health.database}
                    color={health.database === 'connected' ? 'success' : 'error'}
                    size="small"
                  />
                </Box>
              </Box>
            )}
          </CardContent>
        </Card>
      </Box>
    </Container>
  )
}

export default HomePage