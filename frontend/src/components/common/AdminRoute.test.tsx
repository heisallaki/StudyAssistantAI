import { render, screen } from '@testing-library/react'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import { describe, expect, it, vi } from 'vitest'
import AdminRoute from './AdminRoute'
import { useAuth } from '../../hooks/useAuth'

vi.mock('../../hooks/useAuth')

const mockedUseAuth = vi.mocked(useAuth)

function renderAdminRoute() {
  return render(
    <MemoryRouter initialEntries={['/admin']}>
      <Routes>
        <Route path="/login" element={<div>Login page</div>} />
        <Route path="/" element={<div>Dashboard page</div>} />
        <Route element={<AdminRoute />}>
          <Route path="/admin" element={<div>Admin page</div>} />
        </Route>
      </Routes>
    </MemoryRouter>
  )
}

describe('AdminRoute', () => {
  it('shows a loading spinner while auth state is loading', () => {
    mockedUseAuth.mockReturnValue({
      user: null,
      isLoading: true,
      isAuthenticated: false,
      login: vi.fn(),
      register: vi.fn(),
      logout: vi.fn(),
    })

    renderAdminRoute()

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

    renderAdminRoute()

    expect(screen.getByText('Login page')).toBeInTheDocument()
  })

  it('redirects to the dashboard when authenticated but not an admin', () => {
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

    renderAdminRoute()

    expect(screen.getByText('Dashboard page')).toBeInTheDocument()
  })

  it('renders the admin content when authenticated as an admin', () => {
    mockedUseAuth.mockReturnValue({
      user: {
        id: '1',
        email: 'admin@example.com',
        is_active: true,
        is_superuser: true,
        created_at: '2026-01-01T00:00:00Z',
      },
      isLoading: false,
      isAuthenticated: true,
      login: vi.fn(),
      register: vi.fn(),
      logout: vi.fn(),
    })

    renderAdminRoute()

    expect(screen.getByText('Admin page')).toBeInTheDocument()
  })
})