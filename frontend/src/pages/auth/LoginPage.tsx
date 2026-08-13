import { useState } from 'react'
import type { FormEvent } from 'react'
import { Link as RouterLink, useNavigate } from 'react-router-dom'
import { Alert, Box, Button, Card, CardContent, Container, Link, TextField, Typography } from '@mui/material'
import type { AxiosError } from 'axios'
import { useAuth } from '../../hooks/useAuth'

function LoginPage() {
  const { login } = useAuth()
  const navigate = useNavigate()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setError(null)
    setIsSubmitting(true)
    try {
      await login({ email, password })
      navigate('/')
    } catch (err) {
      const axiosError = err as AxiosError<{ detail?: string }>
      setError(axiosError.response?.data?.detail || 'Unable to sign in. Please try again.')
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <Container maxWidth="xs">
      <Box sx={{ display: 'flex', flexDirection: 'column', justifyContent: 'center', minHeight: '100vh' }}>
        <Card>
          <CardContent>
            <Typography variant="h5" component="h1" gutterBottom sx={{ fontWeight: 600 }}>
              Sign in
            </Typography>
            {error && (
              <Alert severity="error" sx={{ mb: 2 }}>
                {error}
              </Alert>
            )}
            <Box component="form" onSubmit={handleSubmit} sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
              <TextField
                label="Email"
                type="email"
                value={email}
                onChange={(event) => setEmail(event.target.value)}
                required
                fullWidth
              />
              <TextField
                label="Password"
                type="password"
                value={password}
                onChange={(event) => setPassword(event.target.value)}
                required
                fullWidth
              />
              <Button type="submit" variant="contained" disabled={isSubmitting} fullWidth>
                {isSubmitting ? 'Signing in...' : 'Sign in'}
              </Button>
            </Box>
            <Typography variant="body2" sx={{ mt: 2 }}>
              Don't have an account? <Link component={RouterLink} to="/register">Create one</Link>
            </Typography>
          </CardContent>
        </Card>
      </Box>
    </Container>
  )
}

export default LoginPage