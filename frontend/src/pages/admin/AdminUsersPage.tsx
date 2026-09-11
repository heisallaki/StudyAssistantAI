import { useEffect, useState } from 'react'
import type { FormEvent } from 'react'
import {
  Alert,
  Box,
  Chip,
  CircularProgress,
  Container,
  Dialog,
  DialogActions,
  DialogContent,
  DialogContentText,
  DialogTitle,
  IconButton,
  MenuItem,
  Pagination,
  Paper,
  Stack,
  Switch,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TextField,
  Tooltip,
  Typography,
  Button,
} from '@mui/material'
import DeleteIcon from '@mui/icons-material/Delete'
import * as adminService from '../../services/adminService'
import { useAuth } from '../../hooks/useAuth'
import type { AdminUser } from '../../types/admin'

const PAGE_SIZE = 20

type ActiveFilter = 'all' | 'active' | 'inactive'
type RoleFilter = 'all' | 'admin' | 'user'

function AdminUsersPage() {
  const { user: currentUser } = useAuth()

  const [users, setUsers] = useState<AdminUser[]>([])
  const [total, setTotal] = useState(0)
  const [totalPages, setTotalPages] = useState(0)
  const [page, setPage] = useState(1)

  const [searchInput, setSearchInput] = useState('')
  const [search, setSearch] = useState('')
  const [activeFilter, setActiveFilter] = useState<ActiveFilter>('all')
  const [roleFilter, setRoleFilter] = useState<RoleFilter>('all')

  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [actionError, setActionError] = useState<string | null>(null)
  const [pendingUserId, setPendingUserId] = useState<string | null>(null)
  const [deleteTarget, setDeleteTarget] = useState<AdminUser | null>(null)
  const [isDeleting, setIsDeleting] = useState(false)

  useEffect(() => {
    let cancelled = false

    async function loadUsers() {
      setIsLoading(true)
      setError(null)

      try {
        const data = await adminService.listUsers({
          search: search || undefined,
          is_active: activeFilter === 'all' ? undefined : activeFilter === 'active',
          is_superuser: roleFilter === 'all' ? undefined : roleFilter === 'admin',
          page,
          page_size: PAGE_SIZE,
        })

        if (!cancelled) {
          setUsers(data.items)
          setTotal(data.total)
          setTotalPages(data.total_pages)
        }
      } catch {
        if (!cancelled) {
          setError('Unable to load users.')
        }
      } finally {
        if (!cancelled) {
          setIsLoading(false)
        }
      }
    }

    loadUsers()

    return () => {
      cancelled = true
    }
  }, [search, activeFilter, roleFilter, page])

  function handleSearchSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setPage(1)
    setSearch(searchInput.trim())
  }

  async function refreshUsers() {
    const data = await adminService.listUsers({
      search: search || undefined,
      is_active: activeFilter === 'all' ? undefined : activeFilter === 'active',
      is_superuser: roleFilter === 'all' ? undefined : roleFilter === 'admin',
      page,
      page_size: PAGE_SIZE,
    })
    setUsers(data.items)
    setTotal(data.total)
    setTotalPages(data.total_pages)
  }

  async function handleToggleActive(targetUser: AdminUser) {
    setActionError(null)
    setPendingUserId(targetUser.id)

    try {
      await adminService.updateUser(targetUser.id, { is_active: !targetUser.is_active })
      await refreshUsers()
    } catch {
      setActionError('Unable to update this user. They may be the last remaining administrator, or you cannot modify your own account this way.')
    } finally {
      setPendingUserId(null)
    }
  }

  async function handleToggleAdmin(targetUser: AdminUser) {
    setActionError(null)
    setPendingUserId(targetUser.id)

    try {
      await adminService.updateUser(targetUser.id, { is_superuser: !targetUser.is_superuser })
      await refreshUsers()
    } catch {
      setActionError('Unable to update this user. They may be the last remaining administrator, or you cannot modify your own account this way.')
    } finally {
      setPendingUserId(null)
    }
  }

  async function handleConfirmDelete() {
    if (!deleteTarget) {
      return
    }

    setActionError(null)
    setIsDeleting(true)

    try {
      await adminService.deleteUser(deleteTarget.id)
      setDeleteTarget(null)
      if (users.length === 1 && page > 1) {
        setPage(page - 1)
      } else {
        await refreshUsers()
      }
    } catch {
      setActionError('Unable to delete this user. They may be the last remaining administrator, or you cannot delete your own account.')
    } finally {
      setIsDeleting(false)
    }
  }

  return (
    <Container maxWidth="lg">
      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3, py: 4 }}>
        <Typography variant="h4" component="h1" sx={{ fontWeight: 600 }}>
          User Management
        </Typography>

        <Box
          component="form"
          onSubmit={handleSearchSubmit}
          sx={{ display: 'flex', flexWrap: 'wrap', gap: 2, alignItems: 'center' }}
        >
          <TextField
            label="Search by email"
            value={searchInput}
            onChange={(event) => setSearchInput(event.target.value)}
            size="small"
            sx={{ minWidth: 240 }}
          />

          <TextField
            select
            label="Status"
            value={activeFilter}
            onChange={(event) => {
              setPage(1)
              setActiveFilter(event.target.value as ActiveFilter)
            }}
            size="small"
            sx={{ minWidth: 160 }}
          >
            <MenuItem value="all">All statuses</MenuItem>
            <MenuItem value="active">Active</MenuItem>
            <MenuItem value="inactive">Inactive</MenuItem>
          </TextField>

          <TextField
            select
            label="Role"
            value={roleFilter}
            onChange={(event) => {
              setPage(1)
              setRoleFilter(event.target.value as RoleFilter)
            }}
            size="small"
            sx={{ minWidth: 160 }}
          >
            <MenuItem value="all">All roles</MenuItem>
            <MenuItem value="admin">Administrators</MenuItem>
            <MenuItem value="user">Regular users</MenuItem>
          </TextField>

          <Button type="submit" variant="outlined">
            Search
          </Button>
        </Box>

        {error && <Alert severity="error">{error}</Alert>}
        {actionError && <Alert severity="error">{actionError}</Alert>}

        {isLoading ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', py: 6 }}>
            <CircularProgress />
          </Box>
        ) : (
          <>
            <Typography variant="body2" color="text.secondary">
              {total} user{total === 1 ? '' : 's'} found
            </Typography>

            <TableContainer component={Paper}>
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TableCell>Email</TableCell>
                    <TableCell>Joined</TableCell>
                    <TableCell align="center">Subjects</TableCell>
                    <TableCell align="center">Documents</TableCell>
                    <TableCell align="center">Quizzes</TableCell>
                    <TableCell align="center">Active</TableCell>
                    <TableCell align="center">Admin</TableCell>
                    <TableCell align="center">Delete</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {users.map((rowUser) => {
                    const isSelf = rowUser.id === currentUser?.id
                    const isPending = pendingUserId === rowUser.id

                    return (
                      <TableRow key={rowUser.id} hover>
                        <TableCell>
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                            {rowUser.email}
                            {isSelf && <Chip label="You" size="small" variant="outlined" />}
                          </Box>
                        </TableCell>
                        <TableCell>{new Date(rowUser.created_at).toLocaleDateString()}</TableCell>
                        <TableCell align="center">{rowUser.subject_count}</TableCell>
                        <TableCell align="center">{rowUser.document_count}</TableCell>
                        <TableCell align="center">{rowUser.quiz_count}</TableCell>
                        <TableCell align="center">
                          <Tooltip title={isSelf ? 'You cannot deactivate your own account' : ''}>
                            <span>
                              <Switch
                                checked={rowUser.is_active}
                                disabled={isSelf || isPending}
                                onChange={() => handleToggleActive(rowUser)}
                                size="small"
                              />
                            </span>
                          </Tooltip>
                        </TableCell>
                        <TableCell align="center">
                          <Tooltip title={isSelf ? 'You cannot revoke your own admin access' : ''}>
                            <span>
                              <Switch
                                checked={rowUser.is_superuser}
                                disabled={isSelf || isPending}
                                onChange={() => handleToggleAdmin(rowUser)}
                                size="small"
                              />
                            </span>
                          </Tooltip>
                        </TableCell>
                        <TableCell align="center">
                          <Tooltip title={isSelf ? 'You cannot delete your own account' : 'Delete user'}>
                            <span>
                              <IconButton
                                size="small"
                                disabled={isSelf || isPending}
                                onClick={() => setDeleteTarget(rowUser)}
                                aria-label={`Delete ${rowUser.email}`}
                              >
                                <DeleteIcon fontSize="small" />
                              </IconButton>
                            </span>
                          </Tooltip>
                        </TableCell>
                      </TableRow>
                    )
                  })}

                  {users.length === 0 && (
                    <TableRow>
                      <TableCell colSpan={8}>
                        <Typography variant="body2" color="text.secondary" sx={{ py: 2, textAlign: 'center' }}>
                          No users match your filters.
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

      <Dialog open={deleteTarget !== null} onClose={() => setDeleteTarget(null)}>
        <DialogTitle>Delete user</DialogTitle>
        <DialogContent>
          <DialogContentText>
            Are you sure you want to permanently delete {deleteTarget?.email}? This will remove all of their
            subjects, documents, quizzes, and other study data. This action cannot be undone.
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteTarget(null)} disabled={isDeleting}>
            Cancel
          </Button>
          <Button onClick={handleConfirmDelete} color="error" variant="contained" disabled={isDeleting}>
            {isDeleting ? 'Deleting...' : 'Delete'}
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  )
}

export default AdminUsersPage