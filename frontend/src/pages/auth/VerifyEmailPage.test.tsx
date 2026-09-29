import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import { AxiosError, AxiosHeaders } from 'axios'
import { describe, expect, it, vi } from 'vitest'
import VerifyEmailPage from './VerifyEmailPage'
import * as authService from '../../services/authService'
import { useAuth } from '../../hooks/useAuth'

vi.mock('../../services/authService')
vi.mock('../../hooks/useAuth')

const mockedAuthService = vi.mocked(authService)
const mockedUseAuth = vi.mocked(useAuth)

function mockAuth(loginWithToken = vi.fn().mockResolvedValue(undefined)) {
  mockedUseAuth.mockReturnValue({
    user: null,
    isLoading: false,
    isAuthenticated: false,
    login: vi.fn(),
    loginWithToken,
    register: vi.fn(),
    logout: vi.fn(),
  })
  return loginWithToken
}

function renderVerifyEmailPage(initialPath = '/verify-email?email=student%40example.com') {
  return render(
    <MemoryRouter initialEntries={[initialPath]}>
      <Routes>
        <Route path="/verify-email" element={<VerifyEmailPage />} />
        <Route path="/" element={<div>Dashboard page</div>} />
      </Routes>
    </MemoryRouter>
  )
}

function axiosErrorWithDetail(detail: unknown): AxiosError<{ detail?: unknown }> {
  return new AxiosError('Request failed', 'ERR_BAD_REQUEST', undefined, undefined, {
    status: 400,
    statusText: 'Bad Request',
    headers: new AxiosHeaders(),
    config: { headers: new AxiosHeaders() },
    data: { detail },
  })
}

describe('VerifyEmailPage', () => {
  it('pre-fills the email from the query string', () => {
    mockAuth()
    renderVerifyEmailPage()
    expect(screen.getByLabelText(/^Email/)).toHaveValue('student@example.com')
  })

  it('submits the code, logs the user in, and redirects to the dashboard on success', async () => {
    const loginWithToken = mockAuth()
    mockedAuthService.verifyEmail.mockResolvedValue({
      access_token: 'issued-access-token',
      token_type: 'bearer',
    })
    const user = userEvent.setup()

    renderVerifyEmailPage()

    await user.type(screen.getByLabelText(/^Verification code/), '123456')
    await user.click(screen.getByRole('button', { name: 'Verify email' }))

    await waitFor(() => {
      expect(mockedAuthService.verifyEmail).toHaveBeenCalledWith({
        email: 'student@example.com',
        code: '123456',
      })
    })
    await waitFor(() => {
      expect(loginWithToken).toHaveBeenCalledWith('issued-access-token')
    })
    expect(await screen.findByText('Dashboard page')).toBeInTheDocument()
  })

  it('shows an error message when the code is incorrect', async () => {
    mockAuth()
    mockedAuthService.verifyEmail.mockRejectedValue(axiosErrorWithDetail('Incorrect verification code.'))
    const user = userEvent.setup()

    renderVerifyEmailPage()

    await user.type(screen.getByLabelText(/^Verification code/), '000000')
    await user.click(screen.getByRole('button', { name: 'Verify email' }))

    expect(await screen.findByText('Incorrect verification code.')).toBeInTheDocument()
  })

  it('resends the code and shows the confirmation message', async () => {
    mockAuth()
    mockedAuthService.resendVerification.mockResolvedValue({
      message: 'If an account with that email exists, a verification code has been sent.',
    })
    const user = userEvent.setup()

    renderVerifyEmailPage()

    await user.click(screen.getByRole('button', { name: 'Resend code' }))

    expect(mockedAuthService.resendVerification).toHaveBeenCalledWith({ email: 'student@example.com' })
    expect(
      await screen.findByText('If an account with that email exists, a verification code has been sent.')
    ).toBeInTheDocument()
  })

  it('only allows digits in the code field, capped at 6 characters', async () => {
    mockAuth()
    const user = userEvent.setup()
    renderVerifyEmailPage()

    const codeField = screen.getByLabelText(/^Verification code/)
    await user.type(codeField, 'ab12cd34ef56')

    expect(codeField).toHaveValue('123456')
  })
})