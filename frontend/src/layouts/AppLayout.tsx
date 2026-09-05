import { Link as RouterLink, Outlet, useLocation } from 'react-router-dom'
import { AppBar, Box, Button, Toolbar, Typography } from '@mui/material'
import { useAuth } from '../hooks/useAuth'

const NAV_LINKS = [
  { to: '/', label: 'Dashboard' },
  { to: '/subjects', label: 'Subjects' },
  { to: '/documents', label: 'Documents' },
  { to: '/tutor', label: 'AI Tutor' },
  { to: '/quizzes', label: 'Quizzes' },
  { to: '/flashcards', label: 'Flashcards' },
  { to: '/planner', label: 'Planner' },
  { to: '/analytics', label: 'Analytics' },
  { to: '/profile', label: 'Profile' },
]

function AppLayout() {
  const { logout } = useAuth()
  const location = useLocation()

  return (
    <Box sx={{ minHeight: '100vh', bgcolor: 'background.default' }}>
      <AppBar position="static" color="default" elevation={0} sx={{ borderBottom: 1, borderColor: 'divider' }}>
        <Toolbar sx={{ gap: 1 }}>
          <Typography variant="h6" sx={{ fontWeight: 700, mr: 3 }}>
            StudyAssistant AI
          </Typography>
          <Box sx={{ display: 'flex', gap: 1, flexGrow: 1 }}>
            {NAV_LINKS.map((link) => {
              const isActive =
                link.to === '/' ? location.pathname === '/' : location.pathname.startsWith(link.to)
              return (
                <Button
                  key={link.to}
                  component={RouterLink}
                  to={link.to}
                  color={isActive ? 'primary' : 'inherit'}
                >
                  {link.label}
                </Button>
              )
            })}
          </Box>
          <Button variant="outlined" color="secondary" onClick={logout}>
            Log out
          </Button>
        </Toolbar>
      </AppBar>
      <Outlet />
    </Box>
  )
}

export default AppLayout