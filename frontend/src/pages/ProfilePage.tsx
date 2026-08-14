import { useEffect, useState } from 'react'
import type { FormEvent } from 'react'
import { Link as RouterLink } from 'react-router-dom'
import {
  Alert,
  Autocomplete,
  Box,
  Button,
  Card,
  CardContent,
  CircularProgress,
  Container,
  Link,
  MenuItem,
  TextField,
  Typography,
} from '@mui/material'
import type { AxiosError } from 'axios'
import * as profileService from '../services/profileService'
import type { AcademicLevel, Profile } from '../types/profile'

const ACADEMIC_LEVEL_OPTIONS: { value: AcademicLevel; label: string }[] = [
  { value: 'high_school', label: 'High School' },
  { value: 'undergraduate', label: 'Undergraduate' },
  { value: 'graduate', label: 'Graduate' },
  { value: 'postgraduate', label: 'Postgraduate' },
  { value: 'other', label: 'Other' },
]

function ProfilePage() {
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

  if (isLoading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '100vh' }}>
        <CircularProgress />
      </Box>
    )
  }

  return (
    <Container maxWidth="sm">
      <Box sx={{ display: 'flex', flexDirection: 'column', justifyContent: 'center', minHeight: '100vh', py: 4 }}>
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
            <Typography variant="body2" sx={{ mt: 2 }}>
              <Link component={RouterLink} to="/">
                Back to home
              </Link>
            </Typography>
            {profile && (
              <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mt: 1 }}>
                Last updated {new Date(profile.updated_at).toLocaleString()}
              </Typography>
            )}
          </CardContent>
        </Card>
      </Box>
    </Container>
  )
}

export default ProfilePage