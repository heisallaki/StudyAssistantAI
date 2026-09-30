import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import { AxiosError, AxiosHeaders } from 'axios'
import { describe, expect, it, vi } from 'vitest'
import ForgotPasswordPage from './ForgotPasswordPage'
import * as authService from '../../services/authService'

vi.mock('../../services/authService')

const mockedAuthService = vi.mocked(authService)

function renderForgotPasswordPage(initialPath = '/forgot-password?email=student%40example.com') {
  return render(
    <MemoryRouter initialEntries={[initialPath]}>
      <Routes>
        <Route path="/forgot-password" element={<ForgotPasswordPage />} />
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

describe('ForgotPasswordPage', () => {
  it('pre-fills the email from the query string', () => {
    renderForgotPasswordPage()
    expect(screen.getByLabelText(/^Email/)).toHaveValue('student@example.com')
  })

  it('requests a reset code and reveals the reset form', async () => {
    mockedAuthService.forgotPassword.mockResolvedValue({
      message: 'If an account with that email exists, a password reset code has been sent.',
    })
    const user = userEvent.setup()

    renderForgotPasswordPage()

    await user.click(screen.getByRole('button', { name: 'Send reset code' }))

    await waitFor(() => {
      expect(mockedAuthService.forgotPassword).toHaveBeenCalledWith({ email: 'student@example.com' })
    })
    expect(
      await screen.findByText('If an account with that email exists, a password reset code has been sent.')
    ).toBeInTheDocument()
    expect(screen.getByLabelText(/^Verification code/)).toBeInTheDocument()
  })

  it('submits the code and new password, then redirects to login', async () => {
    mockedAuthService.forgotPassword.mockResolvedValue({
      message: 'If an account with that email exists, a password reset code has been sent.',
    })
    mockedAuthService.resetPassword.mockResolvedValue({
      message: 'Your password has been reset. You can now sign in with your new password.',
    })
    const user = userEvent.setup()

    renderForgotPasswordPage()

    await user.click(screen.getByRole('button', { name: 'Send reset code' }))
    await screen.findByLabelText(/^Verification code/)

    await user.type(screen.getByLabelText(/^Verification code/), '123456')
    await user.type(screen.getByLabelText(/^New password/), 'N3wSecurePassw0rd!')
    await user.type(screen.getByLabelText(/^Confirm new password/), 'N3wSecurePassw0rd!')
    await user.click(screen.getByRole('button', { name: 'Reset password' }))

    await waitFor(() => {
      expect(mockedAuthService.resetPassword).toHaveBeenCalledWith({
        email: 'student@example.com',
        code: '123456',
        new_password: 'N3wSecurePassw0rd!',
      })
    })
    expect(await screen.findByText('Login page')).toBeInTheDocument()
  })

  it('shows a client-side error when the new passwords do not match', async () => {
    mockedAuthService.forgotPassword.mockResolvedValue({
      message: 'If an account with that email exists, a password reset code has been sent.',
    })
    const user = userEvent.setup()

    renderForgotPasswordPage()

    await user.click(screen.getByRole('button', { name: 'Send reset code' }))
    await screen.findByLabelText(/^Verification code/)

    await user.type(screen.getByLabelText(/^Verification code/), '123456')
    await user.type(screen.getByLabelText(/^New password/), 'N3wSecurePassw0rd!')
    await user.type(screen.getByLabelText(/^Confirm new password/), 'Different1!')
    await user.click(screen.getByRole('button', { name: 'Reset password' }))

    expect(await screen.findByText('Passwords do not match')).toBeInTheDocument()
    expect(mockedAuthService.resetPassword).not.toHaveBeenCalled()
  })

  it('shows an error message when the code is incorrect', async () => {
    mockedAuthService.forgotPassword.mockResolvedValue({
      message: 'If an account with that email exists, a password reset code has been sent.',
    })
    mockedAuthService.resetPassword.mockRejectedValue(axiosErrorWithDetail('Incorrect verification code.'))
    const user = userEvent.setup()

    renderForgotPasswordPage()

    await user.click(screen.getByRole('button', { name: 'Send reset code' }))
    await screen.findByLabelText(/^Verification code/)

    await user.type(screen.getByLabelText(/^Verification code/), '000000')
    await user.type(screen.getByLabelText(/^New password/), 'N3wSecurePassw0rd!')
    await user.type(screen.getByLabelText(/^Confirm new password/), 'N3wSecurePassw0rd!')
    await user.click(screen.getByRole('button', { name: 'Reset password' }))

    expect(await screen.findByText('Incorrect verification code.')).toBeInTheDocument()
  })

  it('only allows digits in the code field, capped at 6 characters', async () => {
    mockedAuthService.forgotPassword.mockResolvedValue({
      message: 'If an account with that email exists, a password reset code has been sent.',
    })
    const user = userEvent.setup()

    renderForgotPasswordPage()

    await user.click(screen.getByRole('button', { name: 'Send reset code' }))
    const codeField = await screen.findByLabelText(/^Verification code/)
    await user.type(codeField, 'ab12cd34ef56')

    expect(codeField).toHaveValue('123456')
  })

  it('lets the user go back and use a different email', async () => {
    mockedAuthService.forgotPassword.mockResolvedValue({
      message: 'If an account with that email exists, a password reset code has been sent.',
    })
    const user = userEvent.setup()

    renderForgotPasswordPage()

    await user.click(screen.getByRole('button', { name: 'Send reset code' }))
    await screen.findByLabelText(/^Verification code/)

    await user.click(screen.getByRole('button', { name: 'Use a different email' }))

    expect(screen.getByRole('button', { name: 'Send reset code' })).toBeInTheDocument()
    expect(screen.getByLabelText(/^Email/)).toHaveValue('student@example.com')
  })
})