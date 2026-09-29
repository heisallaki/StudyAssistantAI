import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import { AxiosError, AxiosHeaders } from 'axios'
import { describe, expect, it, vi } from 'vitest'
import VerifyEmailPage from './VerifyEmailPage'
import * as authService from '../../services/authService'

vi.mock('../../services/authService')

const mockedAuthService = vi.mocked(authService)

function renderVerifyEmailPage(initialPath = '/verify-email?email=student%40example.com') {
  return render(
    <MemoryRouter initialEntries={[initialPath]}>
      <Routes>
        <Route path="/verify-email" element={<VerifyEmailPage />} />
        <Route path="/login" element={<div>Login page</div>} />
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
    renderVerifyEmailPage()
    expect(screen.getByLabelText(/^Email/)).toHaveValue('student@example.com')
  })

  it('submits the code and redirects to login on success', async () => {
    mockedAuthService.verifyEmail.mockResolvedValue({
      id: '1',
      email: 'student@example.com',
      is_active: true,
      is_superuser: false,
      is_email_verified: true,
      created_at: '2026-01-01T00:00:00Z',
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
    expect(await screen.findByText('Login page')).toBeInTheDocument()
  })

  it('shows an error message when the code is incorrect', async () => {
    mockedAuthService.verifyEmail.mockRejectedValue(axiosErrorWithDetail('Incorrect verification code.'))
    const user = userEvent.setup()

    renderVerifyEmailPage()

    await user.type(screen.getByLabelText(/^Verification code/), '000000')
    await user.click(screen.getByRole('button', { name: 'Verify email' }))

    expect(await screen.findByText('Incorrect verification code.')).toBeInTheDocument()
  })

  it('resends the code and shows the confirmation message', async () => {
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
    const user = userEvent.setup()
    renderVerifyEmailPage()

    const codeField = screen.getByLabelText(/^Verification code/)
    await user.type(codeField, 'ab12cd34ef56')

    expect(codeField).toHaveValue('123456')
  })
})