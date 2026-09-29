import { useCallback, useEffect, useState } from 'react'
import { Link as RouterLink, Outlet, useLocation } from 'react-router-dom'
import {
  AppBar,
  Badge,
  Box,
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
import ChevronLeftIcon from '@mui/icons-material/ChevronLeft'
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

const DRAWER_WIDTH = 260
const NAV_DRAWER_STORAGE_KEY = 'studyassistant_nav_drawer_open'

function readStoredDrawerOpen(defaultValue: boolean): boolean {
  const stored = localStorage.getItem(NAV_DRAWER_STORAGE_KEY)
  return stored === 'true' || stored === 'false' ? stored === 'true' : defaultValue
}

function AppLayout() {
  const { logout, user } = useAuth()
  const location = useLocation()
  const theme = useTheme()
  const isMobileNav = useMediaQuery(theme.breakpoints.down('md'))
  const [unreadCount, setUnreadCount] = useState(0)
  const [isDrawerOpen, setIsDrawerOpenState] = useState<boolean>(() => readStoredDrawerOpen(!isMobileNav))

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

  function setIsDrawerOpen(next: boolean) {
    setIsDrawerOpenState(next)
    localStorage.setItem(NAV_DRAWER_STORAGE_KEY, String(next))
  }

  function toggleDrawer() {
    setIsDrawerOpen(!isDrawerOpen)
  }

  function isLinkActive(to: string) {
    return to === '/' ? location.pathname === '/' : location.pathname.startsWith(to)
  }

  const showPersistentDrawer = !isMobileNav && isDrawerOpen

  return (
    <Box sx={{ display: 'flex', minHeight: '100vh', bgcolor: 'background.default' }}>
      <AppBar
        position="fixed"
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
          width: showPersistentDrawer ? { md: `calc(100% - ${DRAWER_WIDTH}px)` } : '100%',
          ml: showPersistentDrawer ? { md: `${DRAWER_WIDTH}px` } : 0,
          transition: theme.transitions.create(['width', 'margin'], {
            easing: theme.transitions.easing.sharp,
            duration: theme.transitions.duration.leavingScreen,
          }),
        }}
      >
        <Toolbar sx={{ gap: { xs: 0.5, sm: 1 }, px: { xs: 1.5, sm: 2, md: 3 } }}>
          <IconButton
            color="inherit"
            aria-label="Toggle navigation menu"
            onClick={toggleDrawer}
            edge="start"
          >
            <MenuIcon />
          </IconButton>

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

          <Box sx={{ flexGrow: 1 }} />

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
          <IconButton
            color="inherit"
            aria-label="Log out"
            onClick={logout}
            sx={{ '&:hover': { color: 'primary.main' } }}
          >
            <LogoutIcon />
          </IconButton>
        </Toolbar>
      </AppBar>

      <Drawer
        anchor="left"
        variant={isMobileNav ? 'temporary' : 'persistent'}
        open={isDrawerOpen}
        onClose={() => setIsDrawerOpen(false)}
        ModalProps={{ keepMounted: true }}
        sx={{
          width: showPersistentDrawer ? DRAWER_WIDTH : 0,
          flexShrink: 0,
          '& .MuiDrawer-paper': { width: DRAWER_WIDTH, boxSizing: 'border-box' },
        }}
      >
        <Box sx={{ width: DRAWER_WIDTH, display: 'flex', flexDirection: 'column', height: '100%' }}>
          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', px: 2, py: 2 }}>
            <Typography
              sx={{
                fontWeight: 800,
                fontSize: '1.15rem',
                background: (t) => getAccentGradient(t.palette.primary.main),
                backgroundClip: 'text',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
                color: 'transparent',
              }}
            >
              StudyAssistant AI
            </Typography>
            <IconButton aria-label="Close navigation menu" onClick={() => setIsDrawerOpen(false)} size="small">
              <ChevronLeftIcon />
            </IconButton>
          </Box>
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
                  onClick={() => {
                    if (isMobileNav) {
                      setIsDrawerOpen(false)
                    }
                  }}
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

      <Box
        component="main"
        sx={{
          flexGrow: 1,
          minWidth: 0,
          transition: theme.transitions.create('margin', {
            easing: theme.transitions.easing.sharp,
            duration: theme.transitions.duration.leavingScreen,
          }),
        }}
      >
        <Toolbar />
        <Outlet />
      </Box>
    </Box>
  )
}

export default AppLayout