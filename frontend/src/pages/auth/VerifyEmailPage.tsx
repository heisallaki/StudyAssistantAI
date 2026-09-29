import { useState } from 'react'
import type { FormEvent } from 'react'
import { Link as RouterLink, useNavigate, useSearchParams } from 'react-router-dom'
import { Alert, Box, Button, Card, CardContent, Container, Link, TextField, Typography } from '@mui/material'
import type { AxiosError } from 'axios'
import * as authService from '../../services/authService'

function extractErrorMessage(err: unknown, fallback: string): string {
  const axiosError = err as AxiosError<{ detail?: unknown }>
  const detail = axiosError.response?.data?.detail

  if (typeof detail === 'string') {
    return detail
  }

  if (Array.isArray(detail)) {
    return detail
      .map((item) => {
        if (typeof item === 'object' && item !== null && 'msg' in item) {
          return String((item as { msg: unknown }).msg)
        }
        return String(item)
      })
      .join(', ')
  }

  return fallback
}

function VerifyEmailPage() {
  const [searchParams] = useSearchParams()
  const navigate = useNavigate()

  const [email, setEmail] = useState(searchParams.get('email') ?? '')
  const [code, setCode] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [infoMessage, setInfoMessage] = useState<string | null>(null)
  const [isVerifying, setIsVerifying] = useState(false)
  const [isResending, setIsResending] = useState(false)

  async function handleVerify(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setError(null)
    setInfoMessage(null)
    setIsVerifying(true)
    try {
      await authService.verifyEmail({ email, code })
      navigate('/login', { state: { verified: true } })
    } catch (err) {
      setError(extractErrorMessage(err, 'Unable to verify your email. Please try again.'))
    } finally {
      setIsVerifying(false)
    }
  }

  async function handleResend() {
    setError(null)
    setInfoMessage(null)
    setIsResending(true)
    try {
      const response = await authService.resendVerification({ email })
      setInfoMessage(response.message)
    } catch (err) {
      setError(extractErrorMessage(err, 'Unable to resend the verification code. Please try again.'))
    } finally {
      setIsResending(false)
    }
  }

  return (
    <Container maxWidth="xs">
      <Box sx={{ display: 'flex', flexDirection: 'column', justifyContent: 'center', minHeight: '100vh' }}>
        <Card>
          <CardContent>
            <Typography variant="h5" component="h1" gutterBottom sx={{ fontWeight: 600 }}>
              Verify your email
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
              We sent a 6-digit code to your email address. Enter it below to activate your account.
            </Typography>
            {error && (
              <Alert severity="error" sx={{ mb: 2 }}>
                {error}
              </Alert>
            )}
            {infoMessage && (
              <Alert severity="success" sx={{ mb: 2 }}>
                {infoMessage}
              </Alert>
            )}
            <Box component="form" onSubmit={handleVerify} sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
              <TextField
                label="Email"
                type="email"
                value={email}
                onChange={(event) => setEmail(event.target.value)}
                required
                fullWidth
              />
              <TextField
                label="Verification code"
                value={code}
                onChange={(event) => setCode(event.target.value.replace(/\D/g, '').slice(0, 6))}
                required
                fullWidth
                slotProps={{ htmlInput: { inputMode: 'numeric', pattern: '[0-9]{6}', maxLength: 6 } }}
                helperText="6-digit code from your email"
              />
              <Button type="submit" variant="contained" disabled={isVerifying || code.length !== 6} fullWidth>
                {isVerifying ? 'Verifying...' : 'Verify email'}
              </Button>
              <Button
                type="button"
                variant="text"
                onClick={handleResend}
                disabled={isResending || !email}
                fullWidth
              >
                {isResending ? 'Sending...' : 'Resend code'}
              </Button>
            </Box>
            <Typography variant="body2" sx={{ mt: 2 }}>
              <Link component={RouterLink} to="/login">
                Back to sign in
              </Link>
            </Typography>
          </CardContent>
        </Card>
      </Box>
    </Container>
  )
}

export default VerifyEmailPage