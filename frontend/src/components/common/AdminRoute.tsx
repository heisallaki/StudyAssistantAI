import { Navigate, Outlet } from 'react-router-dom'
import { createElement } from 'react'
import { Box, CircularProgress } from '@mui/material'
import { useAuth } from '../../hooks/useAuth'

function AdminRoute() {
  const { isAuthenticated, isLoading, user } = useAuth()

  if (isLoading) {
    return createElement(
      Box,
      { sx: { display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '100vh' } },
      createElement(CircularProgress),
    )
  }

  if (!isAuthenticated) {
    return createElement(Navigate, { to: '/login', replace: true })
  }

  if (!user?.is_superuser) {
    return createElement(Navigate, { to: '/', replace: true })
  }

  return createElement(Outlet)
}

export default AdminRoute