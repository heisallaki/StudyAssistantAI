import { useEffect, useState } from 'react'
import {
  Alert,
  Box,
  Chip,
  CircularProgress,
  Container,
  Pagination,
  Paper,
  Stack,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Typography,
} from '@mui/material'
import * as auditLogService from '../../services/auditLogService'
import type { AuditLogEntry } from '../../types/auditLog'

const PAGE_SIZE = 20

const ACTION_LABELS: Record<string, string> = {
  activate_user: 'Activated user',
  deactivate_user: 'Deactivated user',
  grant_admin: 'Granted admin access',
  revoke_admin: 'Revoked admin access',
  delete_user: 'Deleted user',
}

const ACTION_COLORS: Record<string, 'success' | 'warning' | 'error' | 'default'> = {
  activate_user: 'success',
  deactivate_user: 'warning',
  grant_admin: 'success',
  revoke_admin: 'warning',
  delete_user: 'error',
}

function AdminAuditLogPage() {
  const [entries, setEntries] = useState<AuditLogEntry[]>([])
  const [total, setTotal] = useState(0)
  const [totalPages, setTotalPages] = useState(0)
  const [page, setPage] = useState(1)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let cancelled = false

    async function loadEntries() {
      setIsLoading(true)
      setError(null)

      try {
        const data = await auditLogService.listAuditLog(page, PAGE_SIZE)
        if (!cancelled) {
          setEntries(data.items)
          setTotal(data.total)
          setTotalPages(data.total_pages)
        }
      } catch {
        if (!cancelled) {
          setError('Unable to load the audit log.')
        }
      } finally {
        if (!cancelled) {
          setIsLoading(false)
        }
      }
    }

    loadEntries()

    return () => {
      cancelled = true
    }
  }, [page])

  return (
    <Container maxWidth="lg">
      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3, py: 4 }}>
        <Typography variant="h4" component="h1" sx={{ fontWeight: 600 }}>
          Audit Log
        </Typography>

        {error && <Alert severity="error">{error}</Alert>}

        {isLoading ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', py: 6 }}>
            <CircularProgress />
          </Box>
        ) : (
          <>
            <Typography variant="body2" color="text.secondary">
              {total} action{total === 1 ? '' : 's'} recorded
            </Typography>

            <TableContainer component={Paper}>
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TableCell>When</TableCell>
                    <TableCell>Administrator</TableCell>
                    <TableCell>Action</TableCell>
                    <TableCell>Target user</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {entries.map((entry) => (
                    <TableRow key={entry.id} hover>
                      <TableCell>{new Date(entry.created_at).toLocaleString()}</TableCell>
                      <TableCell>{entry.actor_email}</TableCell>
                      <TableCell>
                        <Chip
                          label={ACTION_LABELS[entry.action] ?? entry.action}
                          size="small"
                          color={ACTION_COLORS[entry.action] ?? 'default'}
                          variant="outlined"
                        />
                      </TableCell>
                      <TableCell>{entry.target_email ?? '—'}</TableCell>
                    </TableRow>
                  ))}

                  {entries.length === 0 && (
                    <TableRow>
                      <TableCell colSpan={4}>
                        <Typography variant="body2" color="text.secondary" sx={{ py: 2, textAlign: 'center' }}>
                          No administrator actions recorded yet.
                        </Typography>
                      </TableCell>
                    </TableRow>
                  )}
                </TableBody>
              </Table>
            </TableContainer>

            {totalPages > 1 && (
              <Stack sx={{ alignItems: 'center' }}>
                <Pagination
                  count={totalPages}
                  page={page}
                  onChange={(_event, value) => setPage(value)}
                  color="primary"
                />
              </Stack>
            )}
          </>
        )}
      </Box>
    </Container>
  )
}

export default AdminAuditLogPage