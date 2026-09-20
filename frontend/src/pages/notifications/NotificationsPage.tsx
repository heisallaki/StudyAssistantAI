import { useCallback, useEffect, useState } from 'react'
import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  Chip,
  CircularProgress,
  Container,
  IconButton,
  ToggleButton,
  ToggleButtonGroup,
  Typography,
} from '@mui/material'
import CalendarMonthIcon from '@mui/icons-material/CalendarMonth'
import DeleteIcon from '@mui/icons-material/Delete'
import InfoIcon from '@mui/icons-material/Info'
import MarkEmailReadIcon from '@mui/icons-material/MarkEmailRead'
import QuizIcon from '@mui/icons-material/Quiz'
import ScheduleIcon from '@mui/icons-material/Schedule'
import * as notificationService from '../../services/notificationService'
import type { Notification, NotificationType } from '../../types/notification'

const TYPE_ICON: Record<NotificationType, typeof ScheduleIcon> = {
  study_reminder: ScheduleIcon,
  deadline_reminder: CalendarMonthIcon,
  quiz_reminder: QuizIcon,
  system: InfoIcon,
}

const TYPE_LABEL: Record<NotificationType, string> = {
  study_reminder: 'Study reminder',
  deadline_reminder: 'Deadline reminder',
  quiz_reminder: 'Quiz reminder',
  system: 'System',
}

function formatDateTime(value: string): string {
  return new Date(value).toLocaleString(undefined, {
    month: 'short',
    day: 'numeric',
    hour: 'numeric',
    minute: '2-digit',
  })
}

function NotificationsPage() {
  const [notifications, setNotifications] = useState<Notification[]>([])
  const [filter, setFilter] = useState<'all' | 'unread'>('all')
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const loadNotifications = useCallback(async () => {
    setIsLoading(true)
    try {
      const data = await notificationService.listNotifications(filter === 'unread')
      setNotifications(data)
      setError(null)
    } catch {
      setError('Unable to load your notifications.')
    } finally {
      setIsLoading(false)
    }
  }, [filter])

  useEffect(() => {
    const timeoutId = window.setTimeout(() => {
      void loadNotifications()
    }, 0)
    return () => window.clearTimeout(timeoutId)
  }, [loadNotifications])

  async function handleToggleRead(notification: Notification) {
    await notificationService.setRead(notification.id, !notification.is_read)
    await loadNotifications()
  }

  async function handleDelete(notificationId: string) {
    await notificationService.deleteNotification(notificationId)
    await loadNotifications()
  }

  async function handleMarkAllRead() {
    await notificationService.markAllRead()
    await loadNotifications()
  }

  const hasUnread = notifications.some((notification) => !notification.is_read)

  return (
    <Container maxWidth="sm">
      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3, py: 4 }}>
        <Box
          sx={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            flexWrap: 'wrap',
            gap: 1,
          }}
        >
          <Typography variant="h4" component="h1" sx={{ fontWeight: 600 }}>
            Notifications
          </Typography>
          <Button
            variant="outlined"
            startIcon={<MarkEmailReadIcon />}
            onClick={handleMarkAllRead}
            disabled={!hasUnread}
          >
            Mark all read
          </Button>
        </Box>

        <ToggleButtonGroup
          value={filter}
          exclusive
          onChange={(_event, value) => value && setFilter(value)}
          size="small"
        >
          <ToggleButton value="all">All</ToggleButton>
          <ToggleButton value="unread">Unread</ToggleButton>
        </ToggleButtonGroup>

        {error && <Alert severity="error">{error}</Alert>}

        {isLoading ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', py: 6 }}>
            <CircularProgress />
          </Box>
        ) : notifications.length === 0 ? (
          <Card>
            <CardContent>
              <Typography variant="body2" color="text.secondary">
                {filter === 'unread' ? "You're all caught up." : 'No notifications yet.'}
              </Typography>
            </CardContent>
          </Card>
        ) : (
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1.5 }}>
            {notifications.map((notification) => {
              const Icon = TYPE_ICON[notification.notification_type]
              return (
                <Card
                  key={notification.id}
                  variant="outlined"
                  sx={{ bgcolor: notification.is_read ? 'transparent' : 'action.hover' }}
                >
                  <CardContent sx={{ display: 'flex', gap: 1.5, alignItems: 'flex-start' }}>
                    <Icon color={notification.is_read ? 'disabled' : 'primary'} sx={{ mt: 0.5 }} />
                    <Box sx={{ flexGrow: 1 }}>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, flexWrap: 'wrap' }}>
                        <Typography variant="body2" sx={{ fontWeight: notification.is_read ? 400 : 700 }}>
                          {notification.title}
                        </Typography>
                        <Chip label={TYPE_LABEL[notification.notification_type]} size="small" variant="outlined" />
                      </Box>
                      <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>
                        {notification.message}
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        {formatDateTime(notification.created_at)}
                      </Typography>
                    </Box>
                    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 0.5 }}>
                      <Button size="small" onClick={() => handleToggleRead(notification)}>
                        {notification.is_read ? 'Mark unread' : 'Mark read'}
                      </Button>
                      <IconButton
                        size="small"
                        onClick={() => handleDelete(notification.id)}
                        aria-label="Delete notification"
                      >
                        <DeleteIcon fontSize="small" />
                      </IconButton>
                    </Box>
                  </CardContent>
                </Card>
              )
            })}
          </Box>
        )}
      </Box>
    </Container>
  )
}

export default NotificationsPage