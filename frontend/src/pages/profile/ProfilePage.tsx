import { useEffect, useState } from 'react'
import type { FormEvent } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  Alert,
  Autocomplete,
  Box,
  Button,
  Card,
  CardContent,
  Chip,
  CircularProgress,
  Container,
  Divider,
  MenuItem,
  TextField,
  Typography,
} from '@mui/material'
import type { AxiosError } from 'axios'
import * as profileService from '../../services/profileService'
import * as authService from '../../services/authService'
import { useAuth } from '../../hooks/useAuth'
import type { AcademicLevel, Profile } from '../../types/profile'

const ACADEMIC_LEVEL_OPTIONS: { value: AcademicLevel; label: string }[] = [
  { value: 'high_school', label: 'High School' },
  { value: 'undergraduate', label: 'Undergraduate' },
  { value: 'graduate', label: 'Graduate' },
  { value: 'postgraduate', label: 'Postgraduate' },
  { value: 'other', label: 'Other' },
]

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

function ProfilePage() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  const [profile, setProfile] = useState<Profile | null>(null)
  const [fullName, setFullName] = useState('')
  const [academicLevel, setAcademicLevel] = useState<AcademicLevel | ''>('')
  const [institution, setInstitution] = useState('')
  const [program, setProgram] = useState('')
  const [subjects, setSubjects] = useState<string[]>([])
  const [academicGoals, setAcademicGoals] = useState('')

  const [isLoading, setIsLoading] = useState(true)
  const [isSaving, setIsSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [successMessage, setSuccessMessage] = useState<string | null>(null)

  const [isResendingVerification, setIsResendingVerification] = useState(false)
  const [resendError, setResendError] = useState<string | null>(null)
  const [resendMessage, setResendMessage] = useState<string | null>(null)

  const [isRequestingPasswordOtp, setIsRequestingPasswordOtp] = useState(false)
  const [passwordOtpRequested, setPasswordOtpRequested] = useState(false)
  const [passwordOtpError, setPasswordOtpError] = useState<string | null>(null)
  const [passwordOtpMessage, setPasswordOtpMessage] = useState<string | null>(null)

  const [currentPassword, setCurrentPassword] = useState('')
  const [newPassword, setNewPassword] = useState('')
  const [confirmNewPassword, setConfirmNewPassword] = useState('')
  const [passwordChangeCode, setPasswordChangeCode] = useState('')
  const [isChangingPassword, setIsChangingPassword] = useState(false)
  const [passwordChangeError, setPasswordChangeError] = useState<string | null>(null)
  const [passwordChangeMessage, setPasswordChangeMessage] = useState<string | null>(null)

  const [isRequestingDeletionOtp, setIsRequestingDeletionOtp] = useState(false)
  const [deletionOtpRequested, setDeletionOtpRequested] = useState(false)
  const [deletionOtpError, setDeletionOtpError] = useState<string | null>(null)
  const [deletionOtpMessage, setDeletionOtpMessage] = useState<string | null>(null)

  const [deletionCode, setDeletionCode] = useState('')
  const [deletionConfirmText, setDeletionConfirmText] = useState('')
  const [isDeletingAccount, setIsDeletingAccount] = useState(false)
  const [deletionError, setDeletionError] = useState<string | null>(null)

  useEffect(() => {
    profileService
      .getProfile()
      .then((data) => {
        setProfile(data)
        setFullName(data.full_name ?? '')
        setAcademicLevel(data.academic_level ?? '')
        setInstitution(data.institution ?? '')
        setProgram(data.program ?? '')
        setSubjects(data.subjects)
        setAcademicGoals(data.academic_goals ?? '')
      })
      .catch(() => setError('Unable to load your profile.'))
      .finally(() => setIsLoading(false))
  }, [])

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setError(null)
    setSuccessMessage(null)
    setIsSaving(true)
    try {
      const updated = await profileService.updateProfile({
        full_name: fullName || null,
        academic_level: academicLevel || null,
        institution: institution || null,
        program: program || null,
        subjects,
        academic_goals: academicGoals || null,
      })
      setProfile(updated)
      setSuccessMessage('Profile saved.')
    } catch (err) {
      const axiosError = err as AxiosError<{ detail?: string }>
      setError(axiosError.response?.data?.detail || 'Unable to save your profile. Please try again.')
    } finally {
      setIsSaving(false)
    }
  }

  async function handleResendVerification() {
    if (!user) {
      return
    }
    setResendError(null)
    setResendMessage(null)
    setIsResendingVerification(true)
    try {
      const response = await authService.resendVerification({ email: user.email })
      setResendMessage(response.message)
    } catch (err) {
      setResendError(extractErrorMessage(err, 'Unable to resend the verification code. Please try again.'))
    } finally {
      setIsResendingVerification(false)
    }
  }

  async function handleRequestPasswordOtp() {
    setPasswordOtpError(null)
    setPasswordOtpMessage(null)
    setIsRequestingPasswordOtp(true)
    try {
      const response = await authService.requestPasswordChangeOtp()
      setPasswordOtpMessage(response.message)
      setPasswordOtpRequested(true)
    } catch (err) {
      setPasswordOtpError(extractErrorMessage(err, 'Unable to send a verification code. Please try again.'))
    } finally {
      setIsRequestingPasswordOtp(false)
    }
  }

  async function handleChangePassword(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setPasswordChangeError(null)
    setPasswordChangeMessage(null)

    if (newPassword !== confirmNewPassword) {
      setPasswordChangeError('New passwords do not match')
      return
    }

    setIsChangingPassword(true)
    try {
      const response = await authService.changePassword({
        current_password: currentPassword,
        new_password: newPassword,
        code: passwordChangeCode,
      })
      setPasswordChangeMessage(response.message)
      setCurrentPassword('')
      setNewPassword('')
      setConfirmNewPassword('')
      setPasswordChangeCode('')
      setPasswordOtpRequested(false)
      setPasswordOtpMessage(null)
    } catch (err) {
      setPasswordChangeError(extractErrorMessage(err, 'Unable to change your password. Please try again.'))
    } finally {
      setIsChangingPassword(false)
    }
  }

  async function handleRequestDeletionOtp() {
    setDeletionOtpError(null)
    setDeletionOtpMessage(null)
    setIsRequestingDeletionOtp(true)
    try {
      const response = await authService.requestAccountDeletionOtp()
      setDeletionOtpMessage(response.message)
      setDeletionOtpRequested(true)
    } catch (err) {
      setDeletionOtpError(extractErrorMessage(err, 'Unable to send a verification code. Please try again.'))
    } finally {
      setIsRequestingDeletionOtp(false)
    }
  }

  async function handleDeleteAccount(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setDeletionError(null)
    setIsDeletingAccount(true)
    try {
      await authService.deleteOwnAccount({ code: deletionCode })
      logout()
      navigate('/login')
    } catch (err) {
      setDeletionError(extractErrorMessage(err, 'Unable to delete your account. Please try again.'))
    } finally {
      setIsDeletingAccount(false)
    }
  }

  if (isLoading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '60vh' }}>
        <CircularProgress />
      </Box>
    )
  }

  return (
    <Container maxWidth="sm">
      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, py: 4 }}>
        <Card>
          <CardContent>
            <Typography variant="h5" component="h1" gutterBottom sx={{ fontWeight: 600 }}>
              Academic Profile
            </Typography>
            {error && (
              <Alert severity="error" sx={{ mb: 2 }}>
                {error}
              </Alert>
            )}
            {successMessage && (
              <Alert severity="success" sx={{ mb: 2 }}>
                {successMessage}
              </Alert>
            )}
            <Box component="form" onSubmit={handleSubmit} sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
              <TextField
                label="Full name"
                value={fullName}
                onChange={(event) => setFullName(event.target.value)}
                fullWidth
              />
              <TextField
                select
                label="Academic level"
                value={academicLevel}
                onChange={(event) => setAcademicLevel(event.target.value as AcademicLevel)}
                fullWidth
              >
                <MenuItem value="">Not set</MenuItem>
                {ACADEMIC_LEVEL_OPTIONS.map((option) => (
                  <MenuItem key={option.value} value={option.value}>
                    {option.label}
                  </MenuItem>
                ))}
              </TextField>
              <TextField
                label="Institution"
                value={institution}
                onChange={(event) => setInstitution(event.target.value)}
                fullWidth
              />
              <TextField
                label="Program"
                value={program}
                onChange={(event) => setProgram(event.target.value)}
                fullWidth
              />
              <Autocomplete
                multiple
                freeSolo
                options={[]}
                value={subjects}
                onChange={(_event, newValue) => setSubjects(newValue)}
                renderInput={(params) => (
                  <TextField {...params} label="Subjects" placeholder="Type a subject and press Enter" />
                )}
              />
              <TextField
                label="Academic goals"
                value={academicGoals}
                onChange={(event) => setAcademicGoals(event.target.value)}
                multiline
                minRows={3}
                fullWidth
              />
              <Button type="submit" variant="contained" disabled={isSaving} fullWidth>
                {isSaving ? 'Saving...' : 'Save profile'}
              </Button>
            </Box>
            {profile && (
              <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mt: 2 }}>
                Last updated {new Date(profile.updated_at).toLocaleString()}
              </Typography>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardContent>
            <Typography variant="h5" component="h2" gutterBottom sx={{ fontWeight: 600 }}>
              Account Security
            </Typography>

            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
              <Typography variant="body2" color="text.secondary">
                Email address
              </Typography>
              <Chip
                size="small"
                label={user?.is_email_verified ? 'Verified' : 'Not verified'}
                color={user?.is_email_verified ? 'success' : 'warning'}
              />
            </Box>
            <Typography variant="body2" sx={{ mb: 2 }}>
              {user?.email}
            </Typography>
            {!user?.is_email_verified && (
              <Box sx={{ mb: 3 }}>
                {resendError && (
                  <Alert severity="error" sx={{ mb: 2 }}>
                    {resendError}
                  </Alert>
                )}
                {resendMessage && (
                  <Alert severity="success" sx={{ mb: 2 }}>
                    {resendMessage}
                  </Alert>
                )}
                <Button
                  type="button"
                  variant="outlined"
                  onClick={handleResendVerification}
                  disabled={isResendingVerification}
                >
                  {isResendingVerification ? 'Sending...' : 'Resend verification email'}
                </Button>
              </Box>
            )}

            <Divider sx={{ my: 3 }} />

            <Typography variant="h6" gutterBottom sx={{ fontWeight: 600 }}>
              Change Password
            </Typography>
            {passwordOtpError && (
              <Alert severity="error" sx={{ mb: 2 }}>
                {passwordOtpError}
              </Alert>
            )}
            {passwordChangeError && (
              <Alert severity="error" sx={{ mb: 2 }}>
                {passwordChangeError}
              </Alert>
            )}
            {passwordChangeMessage && (
              <Alert severity="success" sx={{ mb: 2 }}>
                {passwordChangeMessage}
              </Alert>
            )}
            {!passwordOtpRequested ? (
              <Box>
                {passwordOtpMessage && (
                  <Alert severity="success" sx={{ mb: 2 }}>
                    {passwordOtpMessage}
                  </Alert>
                )}
                <Button
                  type="button"
                  variant="outlined"
                  onClick={handleRequestPasswordOtp}
                  disabled={isRequestingPasswordOtp}
                >
                  {isRequestingPasswordOtp ? 'Sending...' : 'Send verification code'}
                </Button>
              </Box>
            ) : (
              <Box
                component="form"
                onSubmit={handleChangePassword}
                sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}
              >
                <TextField
                  label="Current password"
                  type="password"
                  value={currentPassword}
                  onChange={(event) => setCurrentPassword(event.target.value)}
                  required
                  fullWidth
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
                <TextField
                  label="Verification code"
                  value={passwordChangeCode}
                  onChange={(event) => setPasswordChangeCode(event.target.value.replace(/\D/g, '').slice(0, 6))}
                  required
                  fullWidth
                  slotProps={{ htmlInput: { inputMode: 'numeric', pattern: '[0-9]{6}', maxLength: 6 } }}
                  helperText="6-digit code from your email"
                />
                <Button
                  type="submit"
                  variant="contained"
                  disabled={isChangingPassword || passwordChangeCode.length !== 6}
                  fullWidth
                >
                  {isChangingPassword ? 'Changing password...' : 'Change password'}
                </Button>
              </Box>
            )}

            <Divider sx={{ my: 3 }} />

            <Typography variant="h6" gutterBottom sx={{ fontWeight: 600, color: 'error.main' }}>
              Delete Account
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
              This permanently deletes your account and all associated data. This cannot be undone.
            </Typography>
            {deletionOtpError && (
              <Alert severity="error" sx={{ mb: 2 }}>
                {deletionOtpError}
              </Alert>
            )}
            {deletionError && (
              <Alert severity="error" sx={{ mb: 2 }}>
                {deletionError}
              </Alert>
            )}
            {!deletionOtpRequested ? (
              <Box>
                {deletionOtpMessage && (
                  <Alert severity="success" sx={{ mb: 2 }}>
                    {deletionOtpMessage}
                  </Alert>
                )}
                <Button
                  type="button"
                  variant="outlined"
                  color="error"
                  onClick={handleRequestDeletionOtp}
                  disabled={isRequestingDeletionOtp}
                >
                  {isRequestingDeletionOtp ? 'Sending...' : 'Send verification code'}
                </Button>
              </Box>
            ) : (
              <Box
                component="form"
                onSubmit={handleDeleteAccount}
                sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}
              >
                <TextField
                  label="Verification code"
                  value={deletionCode}
                  onChange={(event) => setDeletionCode(event.target.value.replace(/\D/g, '').slice(0, 6))}
                  required
                  fullWidth
                  slotProps={{ htmlInput: { inputMode: 'numeric', pattern: '[0-9]{6}', maxLength: 6 } }}
                  helperText="6-digit code from your email"
                />
                <TextField
                  label='Type "DELETE" to confirm'
                  value={deletionConfirmText}
                  onChange={(event) => setDeletionConfirmText(event.target.value)}
                  required
                  fullWidth
                />
                <Button
                  type="submit"
                  variant="contained"
                  color="error"
                  disabled={isDeletingAccount || deletionCode.length !== 6 || deletionConfirmText !== 'DELETE'}
                  fullWidth
                >
                  {isDeletingAccount ? 'Deleting account...' : 'Delete my account'}
                </Button>
              </Box>
            )}
          </CardContent>
        </Card>
      </Box>
    </Container>
  )
}

export default ProfilePage