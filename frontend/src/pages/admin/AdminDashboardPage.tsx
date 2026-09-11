import { useEffect, useState } from 'react'
import { Link as RouterLink } from 'react-router-dom'
import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  CircularProgress,
  Container,
  Typography,
} from '@mui/material'
import * as adminService from '../../services/adminService'
import type { AdminSystemStats } from '../../types/admin'

interface StatCardProps {
  label: string
  value: number
}

function StatCard({ label, value }: StatCardProps) {
  return (
    <Card sx={{ minWidth: 180, flex: '1 1 180px' }}>
      <CardContent>
        <Typography variant="body2" color="text.secondary">
          {label}
        </Typography>
        <Typography variant="h4" sx={{ fontWeight: 600 }}>
          {value.toLocaleString()}
        </Typography>
      </CardContent>
    </Card>
  )
}

function AdminDashboardPage() {
  const [stats, setStats] = useState<AdminSystemStats | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let cancelled = false

    async function loadStats() {
      setIsLoading(true)
      setError(null)

      try {
        const data = await adminService.getSystemStats()
        if (!cancelled) {
          setStats(data)
        }
      } catch {
        if (!cancelled) {
          setError('Unable to load system statistics.')
        }
      } finally {
        if (!cancelled) {
          setIsLoading(false)
        }
      }
    }

    loadStats()

    return () => {
      cancelled = true
    }
  }, [])

  if (isLoading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '60vh' }}>
        <CircularProgress />
      </Box>
    )
  }

  return (
    <Container maxWidth="lg">
      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3, py: 4 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Typography variant="h4" component="h1" sx={{ fontWeight: 600 }}>
            Administration
          </Typography>

          <Button variant="contained" component={RouterLink} to="/admin/users">
            Manage users
          </Button>
        </Box>

        {error && <Alert severity="error">{error}</Alert>}

        {stats && (
          <>
            <Typography variant="h6">Users</Typography>
            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 2 }}>
              <StatCard label="Total users" value={stats.total_users} />
              <StatCard label="Active users" value={stats.active_users} />
              <StatCard label="Inactive users" value={stats.inactive_users} />
              <StatCard label="Administrators" value={stats.admin_users} />
              <StatCard label="New (last 7 days)" value={stats.new_users_last_7_days} />
              <StatCard label="New (last 30 days)" value={stats.new_users_last_30_days} />
            </Box>

            <Typography variant="h6">Study content</Typography>
            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 2 }}>
              <StatCard label="Subjects" value={stats.total_subjects} />
              <StatCard label="Topics" value={stats.total_topics} />
              <StatCard label="Documents" value={stats.total_documents} />
              <StatCard label="Conversations" value={stats.total_conversations} />
              <StatCard label="Messages" value={stats.total_messages} />
            </Box>

            <Typography variant="h6">Practice &amp; planning</Typography>
            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 2 }}>
              <StatCard label="Quizzes" value={stats.total_quizzes} />
              <StatCard label="Quiz attempts" value={stats.total_quiz_attempts} />
              <StatCard label="Flashcard decks" value={stats.total_flashcard_decks} />
              <StatCard label="Flashcards" value={stats.total_flashcards} />
              <StatCard label="Study goals" value={stats.total_study_goals} />
              <StatCard label="Study sessions" value={stats.total_study_sessions} />
              <StatCard label="Deadlines" value={stats.total_deadlines} />
              <StatCard label="Notifications" value={stats.total_notifications} />
            </Box>
          </>
        )}
      </Box>
    </Container>
  )
}

export default AdminDashboardPage