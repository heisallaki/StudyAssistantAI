import { describe, expect, it, vi } from 'vitest'
import * as adminService from './adminService'
import apiClient from './api'

vi.mock('./api', () => ({
  default: {
    get: vi.fn(),
    patch: vi.fn(),
    delete: vi.fn(),
  },
}))

const mockedApiClient = vi.mocked(apiClient, true)

describe('adminService', () => {
  it('listUsers requests /admin/users with the given filters', async () => {
    mockedApiClient.get.mockResolvedValue({
      data: { items: [], total: 0, page: 1, page_size: 20, total_pages: 0 },
    })

    await adminService.listUsers({ search: 'jane', is_active: true, page: 2, page_size: 10 })

    expect(mockedApiClient.get).toHaveBeenCalledWith('/admin/users', {
      params: { search: 'jane', is_active: true, page: 2, page_size: 10 },
    })
  })

  it('getUser requests /admin/users/{id}', async () => {
    mockedApiClient.get.mockResolvedValue({ data: { id: 'user-1' } })

    await adminService.getUser('user-1')

    expect(mockedApiClient.get).toHaveBeenCalledWith('/admin/users/user-1')
  })

  it('updateUser sends a PATCH with only the changed fields', async () => {
    mockedApiClient.patch.mockResolvedValue({ data: { id: 'user-1', is_active: false } })

    await adminService.updateUser('user-1', { is_active: false })

    expect(mockedApiClient.patch).toHaveBeenCalledWith('/admin/users/user-1', { is_active: false })
  })

  it('deleteUser sends a DELETE for the given id', async () => {
    mockedApiClient.delete.mockResolvedValue({ data: undefined })

    await adminService.deleteUser('user-1')

    expect(mockedApiClient.delete).toHaveBeenCalledWith('/admin/users/user-1')
  })

  it('getSystemStats requests /admin/stats', async () => {
    mockedApiClient.get.mockResolvedValue({ data: { total_users: 5 } })

    const stats = await adminService.getSystemStats()

    expect(mockedApiClient.get).toHaveBeenCalledWith('/admin/stats')
    expect(stats.total_users).toBe(5)
  })
})