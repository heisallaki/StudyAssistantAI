import { render, screen } from '@testing-library/react'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import { describe, expect, it, vi } from 'vitest'
import ProtectedRoute from './ProtectedRoute'
import { useAuth } from '../../hooks/useAuth'

vi.mock('../../hooks/useAuth')

const mockedUseAuth = vi.mocked(useAuth)

function renderProtectedRoute() {
  return render(
    <MemoryRouter initialEntries={['/dashboard']}>
      <Routes>
        <Route path="/login" element={<div>Login page</div>} />
        <Route element={<ProtectedRoute />}>
          <Route path="/dashboard" element={<div>Dashboard page</div>} />
        </Route>
      </Routes>
    </MemoryRouter>
  )
}

describe('ProtectedRoute', () => {
  it('shows a loading spinner while auth state is loading', () => {
    mockedUseAuth.mockReturnValue({
      user: null,
      isLoading: true,
      isAuthenticated: false,
      login: vi.fn(),
      register: vi.fn(),
      logout: vi.fn(),
    })

    renderProtectedRoute()

    expect(screen.getByRole('progressbar')).toBeInTheDocument()
  })

  it('redirects to login when not authenticated', () => {
    mockedUseAuth.mockReturnValue({
      user: null,
      isLoading: false,
      isAuthenticated: false,
      login: vi.fn(),
      register: vi.fn(),
      logout: vi.fn(),
    })

    renderProtectedRoute()

    expect(screen.getByText('Login page')).toBeInTheDocument()
  })

  it('renders the protected content when authenticated', () => {
    mockedUseAuth.mockReturnValue({
      user: {
        id: '1',
        email: 'user@example.com',
        is_active: true,
        is_superuser: false,
        created_at: '2026-01-01T00:00:00Z',
      },
      isLoading: false,
      isAuthenticated: true,
      login: vi.fn(),
      register: vi.fn(),
      logout: vi.fn(),
    })

    renderProtectedRoute()

    expect(screen.getByText('Dashboard page')).toBeInTheDocument()
  })
})