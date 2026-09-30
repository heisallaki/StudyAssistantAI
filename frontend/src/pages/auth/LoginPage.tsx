import { useState } from 'react'
import type { FormEvent } from 'react'
import { Link as RouterLink, useLocation, useNavigate } from 'react-router-dom'
import { Alert, Box, Button, Card, CardContent, Container, Link, TextField, Typography } from '@mui/material'
import type { AxiosError } from 'axios'
import { useAuth } from '../../hooks/useAuth'

function LoginPage() {
  const { login } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [needsVerification, setNeedsVerification] = useState(false)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [passwordResetMessage] = useState<string | null>(() =>
    (location.state as { passwordReset?: boolean } | null)?.passwordReset
      ? 'Your password has been reset. Please sign in with your new password.'
      : null
  )

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setError(null)
    setNeedsVerification(false)
    setIsSubmitting(true)

    try {
      await login({ email, password })
      navigate('/')
    } catch (err) {
      const axiosError = err as AxiosError<{ detail?: unknown }>
      const detail = axiosError.response?.data?.detail

      if (
        typeof detail === 'object' &&
        detail !== null &&
        'error' in detail &&
        (detail as { error?: unknown }).error === 'email_not_verified'
      ) {
        setNeedsVerification(true)
        setError((detail as { message?: string }).message ?? 'Please verify your email address before logging in.')
      } else if (typeof detail === 'string') {
        setError(detail)
      } else if (Array.isArray(detail)) {
        setError(
          detail
            .map((item) => {
              if (
                typeof item === 'object' &&
                item !== null &&
                'msg' in item
              ) {
                return String((item as { msg: unknown }).msg)
              }

              return String(item)
            })
            .join(', ')
        )
      } else {
        setError('Unable to sign in. Please check your email and password.')
      }
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
            {passwordResetMessage && (
              <Alert severity="success" sx={{ mb: 2 }}>
                {passwordResetMessage}
              </Alert>
            )}
            {error && (
              <Alert severity="error" sx={{ mb: 2 }}>
                {error}
                {needsVerification && (
                  <Box sx={{ mt: 1 }}>
                    <Link component={RouterLink} to={`/verify-email?email=${encodeURIComponent(email)}`}>
                      Verify your email
                    </Link>
                  </Box>
                )}
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
              <Box sx={{ textAlign: 'right' }}>
                <Link component={RouterLink} to="/forgot-password" variant="body2">
                  Forgot password?
                </Link>
              </Box>
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