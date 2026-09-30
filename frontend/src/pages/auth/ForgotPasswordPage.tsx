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

function ForgotPasswordPage() {
  const [searchParams] = useSearchParams()
  const navigate = useNavigate()

  const [email, setEmail] = useState(searchParams.get('email') ?? '')
  const [otpRequested, setOtpRequested] = useState(false)
  const [isRequestingOtp, setIsRequestingOtp] = useState(false)
  const [requestError, setRequestError] = useState<string | null>(null)
  const [requestMessage, setRequestMessage] = useState<string | null>(null)

  const [code, setCode] = useState('')
  const [newPassword, setNewPassword] = useState('')
  const [confirmNewPassword, setConfirmNewPassword] = useState('')
  const [isResetting, setIsResetting] = useState(false)
  const [resetError, setResetError] = useState<string | null>(null)

  async function handleRequestOtp(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setRequestError(null)
    setRequestMessage(null)
    setIsRequestingOtp(true)
    try {
      const response = await authService.forgotPassword({ email })
      setRequestMessage(response.message)
      setOtpRequested(true)
    } catch (err) {
      setRequestError(extractErrorMessage(err, 'Unable to send a reset code. Please try again.'))
    } finally {
      setIsRequestingOtp(false)
    }
  }

  async function handleResendOtp() {
    setRequestError(null)
    setRequestMessage(null)
    setIsRequestingOtp(true)
    try {
      const response = await authService.forgotPassword({ email })
      setRequestMessage(response.message)
    } catch (err) {
      setRequestError(extractErrorMessage(err, 'Unable to send a reset code. Please try again.'))
    } finally {
      setIsRequestingOtp(false)
    }
  }

  async function handleResetPassword(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setResetError(null)

    if (newPassword !== confirmNewPassword) {
      setResetError('Passwords do not match')
      return
    }

    setIsResetting(true)
    try {
      await authService.resetPassword({ email, code, new_password: newPassword })
      navigate('/login', { state: { passwordReset: true } })
    } catch (err) {
      setResetError(extractErrorMessage(err, 'Unable to reset your password. Please try again.'))
    } finally {
      setIsResetting(false)
    }
  }

  return (
    <Container maxWidth="xs">
      <Box sx={{ display: 'flex', flexDirection: 'column', justifyContent: 'center', minHeight: '100vh' }}>
        <Card>
          <CardContent>
            <Typography variant="h5" component="h1" gutterBottom sx={{ fontWeight: 600 }}>
              Reset your password
            </Typography>

            {!otpRequested ? (
              <>
                <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                  Enter the email address on your account and we'll send you a code to reset your password.
                </Typography>
                {requestError && (
                  <Alert severity="error" sx={{ mb: 2 }}>
                    {requestError}
                  </Alert>
                )}
                <Box
                  component="form"
                  onSubmit={handleRequestOtp}
                  sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}
                >
                  <TextField
                    label="Email"
                    type="email"
                    value={email}
                    onChange={(event) => setEmail(event.target.value)}
                    required
                    fullWidth
                  />
                  <Button type="submit" variant="contained" disabled={isRequestingOtp} fullWidth>
                    {isRequestingOtp ? 'Sending...' : 'Send reset code'}
                  </Button>
                </Box>
              </>
            ) : (
              <>
                <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                  Enter the 6-digit code we sent to {email} along with your new password.
                </Typography>
                {requestMessage && (
                  <Alert severity="success" sx={{ mb: 2 }}>
                    {requestMessage}
                  </Alert>
                )}
                {resetError && (
                  <Alert severity="error" sx={{ mb: 2 }}>
                    {resetError}
                  </Alert>
                )}
                <Box
                  component="form"
                  onSubmit={handleResetPassword}
                  sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}
                >
                  <TextField
                    label="Verification code"
                    value={code}
                    onChange={(event) => setCode(event.target.value.replace(/\D/g, '').slice(0, 6))}
                    required
                    fullWidth
                    slotProps={{ htmlInput: { inputMode: 'numeric', pattern: '[0-9]{6}', maxLength: 6 } }}
                    helperText="6-digit code from your email"
                  />
                  <TextField
                    label="New password"
                    type="password"
                    value={newPassword}
                    onChange={(event) => setNewPassword(event.target.value)}
                    required
                    fullWidth
                    helperText="At least 8 characters, with uppercase, lowercase, a number, and a special character"
                  />
                  <TextField
                    label="Confirm new password"
                    type="password"
                    value={confirmNewPassword}
                    onChange={(event) => setConfirmNewPassword(event.target.value)}
                    required
                    fullWidth
                  />
                  <Button
                    type="submit"
                    variant="contained"
                    disabled={isResetting || code.length !== 6}
                    fullWidth
                  >
                    {isResetting ? 'Resetting password...' : 'Reset password'}
                  </Button>
                  <Button type="button" variant="text" onClick={handleResendOtp} disabled={isRequestingOtp} fullWidth>
                    {isRequestingOtp ? 'Sending...' : 'Resend code'}
                  </Button>
                  <Button type="button" variant="text" onClick={() => setOtpRequested(false)} fullWidth>
                    Use a different email
                  </Button>
                </Box>
              </>
            )}

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

export default ForgotPasswordPage