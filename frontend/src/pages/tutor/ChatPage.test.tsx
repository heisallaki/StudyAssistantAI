import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import { describe, expect, it, vi } from 'vitest'
import ChatPage from './ChatPage'
import * as tutorService from '../../services/tutorService'
import type { ConversationDetail } from '../../types/tutor'

vi.mock('../../services/tutorService')

const mockedTutorService = vi.mocked(tutorService)

const conversationDetail: ConversationDetail = {
  id: 'conv-1',
  subject_id: null,
  title: 'Financial Management basics',
  mode: 'tutor',
  explanation_level: 'intermediate',
  created_at: '2026-01-01T00:00:00Z',
  updated_at: '2026-01-01T00:00:00Z',
  messages: [],
}

function renderChatPage() {
  return render(
    <MemoryRouter initialEntries={['/tutor/conv-1']}>
      <Routes>
        <Route path="/tutor/:conversationId" element={<ChatPage />} />
        <Route path="/tutor" element={<div>Conversations list page</div>} />
      </Routes>
    </MemoryRouter>
  )
}

describe('ChatPage delete flow', () => {
  it('shows a confirmation dialog naming the conversation before deleting', async () => {
    mockedTutorService.getConversation.mockResolvedValue(conversationDetail)
    const user = userEvent.setup()

    renderChatPage()

    await screen.findByText('Financial Management basics')
    await user.click(screen.getByRole('button', { name: /delete/i }))

    expect(await screen.findByText('Delete "Financial Management basics"?')).toBeInTheDocument()
    expect(mockedTutorService.deleteConversation).not.toHaveBeenCalled()
  })

  it('cancels without deleting when Cancel is clicked', async () => {
    mockedTutorService.getConversation.mockResolvedValue(conversationDetail)
    const user = userEvent.setup()

    renderChatPage()

    await screen.findByText('Financial Management basics')
    await user.click(screen.getByRole('button', { name: /delete/i }))
    await screen.findByText('Delete "Financial Management basics"?')
    await user.click(screen.getByRole('button', { name: 'Cancel' }))

    await waitFor(() => {
      expect(screen.queryByText('Delete "Financial Management basics"?')).not.toBeInTheDocument()
    })
    expect(mockedTutorService.deleteConversation).not.toHaveBeenCalled()
  })

  it('deletes the conversation and navigates back to the conversations list on confirm', async () => {
    mockedTutorService.getConversation.mockResolvedValue(conversationDetail)
    mockedTutorService.deleteConversation.mockResolvedValue(undefined)
    const user = userEvent.setup()

    renderChatPage()

    await screen.findByText('Financial Management basics')
    await user.click(screen.getByRole('button', { name: /delete/i }))
    const dialogDeleteButton = (await screen.findAllByRole('button', { name: 'Delete' })).at(-1)
    if (!dialogDeleteButton) throw new Error('Dialog delete button not found')
    await user.click(dialogDeleteButton)

    await waitFor(() => {
      expect(mockedTutorService.deleteConversation).toHaveBeenCalledWith('conv-1')
    })
    expect(await screen.findByText('Conversations list page')).toBeInTheDocument()
  })

  it('shows an error message and stays on the page when deletion fails', async () => {
    mockedTutorService.getConversation.mockResolvedValue(conversationDetail)
    mockedTutorService.deleteConversation.mockRejectedValue(new Error('network error'))
    const user = userEvent.setup()

    renderChatPage()

    await screen.findByText('Financial Management basics')
    await user.click(screen.getByRole('button', { name: /delete/i }))
    const dialogDeleteButton = (await screen.findAllByRole('button', { name: 'Delete' })).at(-1)
    if (!dialogDeleteButton) throw new Error('Dialog delete button not found')
    await user.click(dialogDeleteButton)

    expect(await screen.findByText('Unable to delete this conversation. Please try again.')).toBeInTheDocument()
    expect(screen.queryByText('Conversations list page')).not.toBeInTheDocument()
  })
})