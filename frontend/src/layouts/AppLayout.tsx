import { useCallback, useEffect, useState } from 'react'
import { Link as RouterLink, Outlet, useLocation } from 'react-router-dom'
import {
  AppBar,
  Badge,
  Box,
  Button,
  Divider,
  Drawer,
  IconButton,
  List,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Toolbar,
  Typography,
  alpha,
  useMediaQuery,
  useTheme,
} from '@mui/material'
import MenuIcon from '@mui/icons-material/Menu'
import LogoutIcon from '@mui/icons-material/Logout'
import NotificationsIcon from '@mui/icons-material/Notifications'
import SearchIcon from '@mui/icons-material/Search'
import { useAuth } from '../hooks/useAuth'
import * as notificationService from '../services/notificationService'
import ThemeSettingsMenu from '../components/common/ThemeSettingsMenu'
import { getAccentGradient, getGlassBackground, getGlassShadow } from '../theme/theme'

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
  const { logout, user } = useAuth()
  const location = useLocation()
  const theme = useTheme()
  const isMobileNav = useMediaQuery(theme.breakpoints.down('md'))
  const [unreadCount, setUnreadCount] = useState(0)
  const [isDrawerOpen, setIsDrawerOpen] = useState(false)

  const navLinks = user?.is_superuser ? [...NAV_LINKS, { to: '/admin', label: 'Admin' }] : NAV_LINKS

  const refreshUnreadCount = useCallback(() => {
    notificationService
      .getUnreadCount()
      .then((data) => setUnreadCount(data.unread_count))
      .catch(() => setUnreadCount(0))
  }, [])

  useEffect(() => {
    refreshUnreadCount()
  }, [refreshUnreadCount, location.pathname])

  function isLinkActive(to: string) {
    return to === '/' ? location.pathname === '/' : location.pathname.startsWith(to)
  }

  return (
    <Box sx={{ minHeight: '100vh', bgcolor: 'background.default' }}>
      <AppBar
        position="sticky"
        color="default"
        elevation={0}
        sx={{
          top: 0,
          bgcolor: (t) => getGlassBackground(t),
          backdropFilter: 'blur(16px)',
          WebkitBackdropFilter: 'blur(16px)',
          borderBottom: '1px solid',
          borderColor: (t) => alpha(t.palette.divider, 0.6),
          boxShadow: (t) => getGlassShadow(t),
        }}
      >
        <Toolbar sx={{ gap: { xs: 0.5, sm: 1 }, px: { xs: 1.5, sm: 2, md: 3 } }}>
          {isMobileNav && (
            <IconButton
              color="inherit"
              aria-label="Open navigation menu"
              onClick={() => setIsDrawerOpen(true)}
              edge="start"
            >
              <MenuIcon />
            </IconButton>
          )}

          <Typography
            component={RouterLink}
            to="/"
            variant="h6"
            sx={{
              fontWeight: 800,
              letterSpacing: '-0.02em',
              mr: { xs: 1, md: 3 },
              fontSize: { xs: '1.05rem', sm: '1.2rem', md: '1.35rem' },
              background: (t) => getAccentGradient(t.palette.primary.main),
              backgroundClip: 'text',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              color: 'transparent',
              textDecoration: 'none',
              whiteSpace: 'nowrap',
            }}
          >
            StudyAssistant AI
          </Typography>

          {!isMobileNav && (
            <Box sx={{ display: 'flex', gap: 0.5, flexGrow: 1, flexWrap: 'wrap' }}>
              {navLinks.map((link) => {
                const isActive = isLinkActive(link.to)
                return (
                  <Button
                    key={link.to}
                    component={RouterLink}
                    to={link.to}
                    disableRipple={false}
                    sx={{
                      color: isActive ? 'primary.main' : 'text.secondary',
                      fontWeight: isActive ? 700 : 500,
                      px: 1.5,
                      borderRadius: 2,
                      position: 'relative',
                      transition: 'background-color 0.15s ease, color 0.15s ease',
                      bgcolor: isActive ? (t) => alpha(t.palette.primary.main, 0.12) : 'transparent',
                      '&:hover': {
                        bgcolor: (t) => alpha(t.palette.primary.main, isActive ? 0.18 : 0.08),
                        color: 'primary.main',
                      },
                      '&::after': {
                        content: '""',
                        position: 'absolute',
                        left: 10,
                        right: 10,
                        bottom: 2,
                        height: 2,
                        borderRadius: 1,
                        bgcolor: isActive ? 'primary.main' : 'transparent',
                      },
                    }}
                  >
                    {link.label}
                  </Button>
                )
              })}
            </Box>
          )}

          {isMobileNav && <Box sx={{ flexGrow: 1 }} />}

          <IconButton
            component={RouterLink}
            to="/search"
            color="inherit"
            aria-label="Search"
            sx={{ '&:hover': { color: 'primary.main' } }}
          >
            <SearchIcon />
          </IconButton>
          <IconButton
            component={RouterLink}
            to="/notifications"
            color="inherit"
            aria-label="Notifications"
            sx={{ '&:hover': { color: 'primary.main' } }}
          >
            <Badge badgeContent={unreadCount} color="error">
              <NotificationsIcon />
            </Badge>
          </IconButton>
          <ThemeSettingsMenu />

          {!isMobileNav && (
            <Button
              variant="outlined"
              color="secondary"
              onClick={logout}
              sx={{ ml: 1, whiteSpace: 'nowrap' }}
            >
              Log out
            </Button>
          )}
        </Toolbar>
      </AppBar>

      <Drawer
        anchor="left"
        open={isMobileNav && isDrawerOpen}
        onClose={() => setIsDrawerOpen(false)}
        ModalProps={{ keepMounted: true }}
      >
        <Box sx={{ width: 260, display: 'flex', flexDirection: 'column', height: '100%' }}>
          <Typography
            sx={{
              fontWeight: 800,
              fontSize: '1.15rem',
              px: 2,
              py: 2,
              background: (t) => getAccentGradient(t.palette.primary.main),
              backgroundClip: 'text',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              color: 'transparent',
            }}
          >
            StudyAssistant AI
          </Typography>
          <Divider />
          <List sx={{ flexGrow: 1 }}>
            {navLinks.map((link) => {
              const isActive = isLinkActive(link.to)
              return (
                <ListItemButton
                  key={link.to}
                  component={RouterLink}
                  to={link.to}
                  selected={isActive}
                  onClick={() => setIsDrawerOpen(false)}
                  sx={{
                    '&.Mui-selected': {
                      bgcolor: (t) => alpha(t.palette.primary.main, 0.14),
                      borderRight: '3px solid',
                      borderColor: 'primary.main',
                    },
                  }}
                >
                  <ListItemText
                    primary={link.label}
                    slotProps={{
                      primary: {
                        sx: { fontWeight: isActive ? 700 : 500, color: isActive ? 'primary.main' : 'text.primary' },
                      },
                    }}
                  />
                </ListItemButton>
              )
            })}
          </List>
          <Divider />
          <List>
            <ListItemButton onClick={logout}>
              <ListItemIcon sx={{ minWidth: 36 }}>
                <LogoutIcon fontSize="small" />
              </ListItemIcon>
              <ListItemText primary="Log out" />
            </ListItemButton>
          </List>
        </Box>
      </Drawer>

      <Outlet />
    </Box>
  )
}

export default AppLayout