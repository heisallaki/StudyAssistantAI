import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { describe, expect, it, vi } from 'vitest'
import RegisterPage from './RegisterPage'
import { useAuth } from '../../hooks/useAuth'

vi.mock('../../hooks/useAuth')

const mockedUseAuth = vi.mocked(useAuth)

function renderRegisterPage() {
  return render(
    <MemoryRouter>
      <RegisterPage />
    </MemoryRouter>
  )
}

function mockAuth(register = vi.fn().mockResolvedValue(undefined)) {
  mockedUseAuth.mockReturnValue({
    user: null,
    isLoading: false,
    isAuthenticated: false,
    login: vi.fn(),
    register,
    logout: vi.fn(),
    loginWithToken: vi.fn(),
  })
  return register
}

describe('RegisterPage', () => {
  it('submits registration when passwords match', async () => {
    const register = mockAuth()

    renderRegisterPage()

    fireEvent.change(screen.getByLabelText(/^Email/), { target: { value: 'new@example.com' } })
    fireEvent.change(screen.getByLabelText(/^Password/), { target: { value: 'S3curePassw0rd!' } })
    fireEvent.change(screen.getByLabelText(/^Confirm password/), { target: { value: 'S3curePassw0rd!' } })
    fireEvent.click(screen.getByRole('button', { name: 'Create account' }))

    await waitFor(() => {
      expect(register).toHaveBeenCalledWith({ email: 'new@example.com', password: 'S3curePassw0rd!' })
    })
  })

  it('shows a client-side error when passwords do not match', () => {
    mockAuth()

    renderRegisterPage()

    fireEvent.change(screen.getByLabelText(/^Email/), { target: { value: 'new@example.com' } })
    fireEvent.change(screen.getByLabelText(/^Password/), { target: { value: 'S3curePassw0rd!' } })
    fireEvent.change(screen.getByLabelText(/^Confirm password/), { target: { value: 'Different1!' } })
    fireEvent.click(screen.getByRole('button', { name: 'Create account' }))

    expect(screen.getByText('Passwords do not match')).toBeInTheDocument()
  })
})