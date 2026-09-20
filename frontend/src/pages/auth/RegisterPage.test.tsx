import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { AxiosError, AxiosHeaders } from 'axios'
import { describe, expect, it, vi } from 'vitest'
import RegisterPage from './RegisterPage'
import { useAuth } from '../../hooks/useAuth'
import type { AuthContextValue } from '../../contexts/AuthContext'

vi.mock('../../hooks/useAuth')

const mockedUseAuth = vi.mocked(useAuth)

function renderRegisterPage() {
  return render(
    <MemoryRouter>
      <RegisterPage />
    </MemoryRouter>
  )
}

function mockAuth(register: AuthContextValue['register']) {
  mockedUseAuth.mockReturnValue({
    user: null,
    isLoading: false,
    isAuthenticated: false,
    login: vi.fn(),
    register,
    logout: vi.fn(),
  })
}

function axiosErrorWithDetail(detail: unknown): AxiosError<{ detail?: unknown }> {
  return new AxiosError(
    'Request failed',
    'ERR_BAD_REQUEST',
    undefined,
    undefined,
    {
      status: 422,
      statusText: 'Unprocessable Entity',
      headers: new AxiosHeaders(),
      config: { headers: new AxiosHeaders() },
      data: { detail },
    }
  )
}

function fillRegistrationForm(
  email: string,
  password: string,
  confirmPassword: string
) {
  fireEvent.change(screen.getByLabelText(/^Email/), {
    target: { value: email },
  })

  fireEvent.change(screen.getByLabelText(/^Password/), {
    target: { value: password },
  })

  fireEvent.change(screen.getByLabelText(/^Confirm password/), {
    target: { value: confirmPassword },
  })
}

function submitRegistrationForm() {
  const button = screen.getByRole('button', { name: 'Create account' })
  const form = button.closest('form')

  if (!form) {
    throw new Error('Registration form was not found')
  }

  fireEvent.submit(form)
}

describe('RegisterPage', () => {
  it('blocks submission when passwords do not match', async () => {
    const register = vi.fn()
    mockAuth(register)

    renderRegisterPage()

    fillRegistrationForm(
      'test@example.com',
      'S3curePassw0rd!',
      'DifferentPassw0rd!'
    )

    submitRegistrationForm()

    expect(await screen.findByText('Passwords do not match')).toBeInTheDocument()
    expect(register).not.toHaveBeenCalled()
  })

  it('submits registration when passwords match', async () => {
    const register = vi.fn().mockResolvedValue(undefined)
    mockAuth(register)

    renderRegisterPage()

    fillRegistrationForm(
      'test@example.com',
      'S3curePassw0rd!',
      'S3curePassw0rd!'
    )

    submitRegistrationForm()

    await waitFor(() => {
      expect(register).toHaveBeenCalledTimes(1)
      expect(register).toHaveBeenCalledWith({
        email: 'test@example.com',
        password: 'S3curePassw0rd!',
      })
    })
  })

  it('renders each password-policy validation message from the API', async () => {
    const register = vi.fn().mockRejectedValue(
      axiosErrorWithDetail([
        { msg: 'Password must contain at least one uppercase letter' },
        { msg: 'Password must contain at least one special character' },
      ])
    )
    mockAuth(register)

    renderRegisterPage()

    fillRegistrationForm(
      'test@example.com',
      'alllowercase1',
      'alllowercase1'
    )

    submitRegistrationForm()

    expect(
      await screen.findByText(
        'Password must contain at least one uppercase letter, Password must contain at least one special character'
      )
    ).toBeInTheDocument()
  })
})