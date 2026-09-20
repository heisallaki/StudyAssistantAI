import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { AxiosError, AxiosHeaders } from 'axios'
import { describe, expect, it, vi } from 'vitest'
import LoginPage from './LoginPage'
import { useAuth } from '../../hooks/useAuth'
import type { AuthContextValue } from '../../contexts/AuthContext'

vi.mock('../../hooks/useAuth')

const mockedUseAuth = vi.mocked(useAuth)

function renderLoginPage() {
  return render(
    <MemoryRouter>
      <LoginPage />
    </MemoryRouter>
  )
}

function mockAuth(login: AuthContextValue['login']) {
  mockedUseAuth.mockReturnValue({
    user: null,
    isLoading: false,
    isAuthenticated: false,
    login,
    register: vi.fn(),
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
      status: 401,
      statusText: 'Unauthorized',
      headers: new AxiosHeaders(),
      config: { headers: new AxiosHeaders() },
      data: { detail },
    }
  )
}

function fillLoginForm(email: string, password: string) {
  fireEvent.change(screen.getByLabelText(/^Email/), {
    target: { value: email },
  })

  fireEvent.change(screen.getByLabelText(/^Password/), {
    target: { value: password },
  })
}

function submitLoginForm() {
  const button = screen.getByRole('button', { name: 'Sign in' })
  const form = button.closest('form')

  if (!form) {
    throw new Error('Login form was not found')
  }

  fireEvent.submit(form)
}

describe('LoginPage', () => {
  it('submits the entered credentials', async () => {
    const login = vi.fn().mockResolvedValue(undefined)
    mockAuth(login)

    renderLoginPage()

    fillLoginForm('test@example.com', 'S3curePassw0rd!')
    submitLoginForm()

    await waitFor(() => {
      expect(login).toHaveBeenCalledTimes(1)
      expect(login).toHaveBeenCalledWith({
        email: 'test@example.com',
        password: 'S3curePassw0rd!',
      })
    })
  })

  it('shows a string error message returned by the API', async () => {
    const login = vi.fn().mockRejectedValue(
      axiosErrorWithDetail('Invalid email or password')
    )
    mockAuth(login)

    renderLoginPage()

    fillLoginForm('test@example.com', 'wrong-password')
    submitLoginForm()

    expect(
      await screen.findByText('Invalid email or password')
    ).toBeInTheDocument()
  })

  it('joins an array-shaped validation error into one message', async () => {
    const login = vi.fn().mockRejectedValue(
      axiosErrorWithDetail([
        { msg: 'Field required' },
        { msg: 'Value is not a valid email address' },
      ])
    )
    mockAuth(login)

    renderLoginPage()

    fillLoginForm('test@example.com', 'S3curePassw0rd!')
    submitLoginForm()

    expect(
      await screen.findByText(
        'Field required, Value is not a valid email address'
      )
    ).toBeInTheDocument()
  })

  it('falls back to a generic message when the API gives no detail', async () => {
    const login = vi.fn().mockRejectedValue(new Error('network down'))
    mockAuth(login)

    renderLoginPage()

    fillLoginForm('test@example.com', 'S3curePassw0rd!')
    submitLoginForm()

    expect(
      await screen.findByText(
        'Unable to sign in. Please check your email and password.'
      )
    ).toBeInTheDocument()
  })
})
