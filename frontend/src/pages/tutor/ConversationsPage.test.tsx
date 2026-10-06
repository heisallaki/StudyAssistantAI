import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router-dom'
import { describe, expect, it, vi } from 'vitest'
import ConversationsPage from './ConversationsPage'
import * as tutorService from '../../services/tutorService'
import * as subjectService from '../../services/subjectService'
import type { Conversation } from '../../types/tutor'

vi.mock('../../services/tutorService')
vi.mock('../../services/subjectService')

const mockedTutorService = vi.mocked(tutorService)
const mockedSubjectService = vi.mocked(subjectService)

const conversations: Conversation[] = [
  {
    id: 'conv-1',
    subject_id: null,
    title: 'Financial Management basics',
    mode: 'tutor',
    explanation_level: 'intermediate',
    created_at: '2026-01-01T00:00:00Z',
    updated_at: '2026-01-01T00:00:00Z',
  },
  {
    id: 'conv-2',
    subject_id: null,
    title: 'Databases 101',
    mode: 'socratic',
    explanation_level: 'beginner',
    created_at: '2026-01-02T00:00:00Z',
    updated_at: '2026-01-02T00:00:00Z',
  },
]

function renderConversationsPage() {
  return render(
    <MemoryRouter>
      <ConversationsPage />
    </MemoryRouter>
  )
}

describe('ConversationsPage delete flow', () => {
  it('shows a confirmation dialog naming the conversation before deleting', async () => {
    mockedTutorService.listConversations.mockResolvedValue(conversations)
    mockedSubjectService.listSubjects.mockResolvedValue([])
    const user = userEvent.setup()

    renderConversationsPage()

    await screen.findByText('Financial Management basics')
    await user.click(screen.getAllByLabelText('Delete conversation')[0])

    expect(await screen.findByText('Delete "Financial Management basics"?')).toBeInTheDocument()
    expect(mockedTutorService.deleteConversation).not.toHaveBeenCalled()
  })

  it('cancels without deleting when Cancel is clicked', async () => {
    mockedTutorService.listConversations.mockResolvedValue(conversations)
    mockedSubjectService.listSubjects.mockResolvedValue([])
    const user = userEvent.setup()

    renderConversationsPage()

    await screen.findByText('Financial Management basics')
    await user.click(screen.getAllByLabelText('Delete conversation')[0])
    await screen.findByText('Delete "Financial Management basics"?')
    await user.click(screen.getByRole('button', { name: 'Cancel' }))

    await waitFor(() => {
      expect(screen.queryByText('Delete "Financial Management basics"?')).not.toBeInTheDocument()
    })
    expect(mockedTutorService.deleteConversation).not.toHaveBeenCalled()
    expect(screen.getByText('Financial Management basics')).toBeInTheDocument()
  })

  it('deletes the conversation and removes it from the list on confirm', async () => {
    mockedTutorService.listConversations.mockResolvedValue(conversations)
    mockedSubjectService.listSubjects.mockResolvedValue([])
    mockedTutorService.deleteConversation.mockResolvedValue(undefined)
    const user = userEvent.setup()

    renderConversationsPage()

    await screen.findByText('Financial Management basics')
    await user.click(screen.getAllByLabelText('Delete conversation')[0])
    await screen.findByText('Delete "Financial Management basics"?')
    await user.click(screen.getByRole('button', { name: 'Delete' }))

    await waitFor(() => {
      expect(mockedTutorService.deleteConversation).toHaveBeenCalledWith('conv-1')
    })
    await waitFor(() => {
      expect(screen.queryByText('Financial Management basics')).not.toBeInTheDocument()
    })
    expect(screen.getByText('Databases 101')).toBeInTheDocument()
  })

  it('shows an error message and keeps the conversation when deletion fails', async () => {
    mockedTutorService.listConversations.mockResolvedValue(conversations)
    mockedSubjectService.listSubjects.mockResolvedValue([])
    mockedTutorService.deleteConversation.mockRejectedValue(new Error('network error'))
    const user = userEvent.setup()

    renderConversationsPage()

    await screen.findByText('Financial Management basics')
    await user.click(screen.getAllByLabelText('Delete conversation')[0])
    await screen.findByText('Delete "Financial Management basics"?')
    await user.click(screen.getByRole('button', { name: 'Delete' }))

    expect(await screen.findByText('Unable to delete this conversation. Please try again.')).toBeInTheDocument()
    expect(screen.getByText('Financial Management basics')).toBeInTheDocument()
  })
})