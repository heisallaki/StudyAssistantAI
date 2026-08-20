import { useEffect, useRef, useState } from 'react'
import type { FormEvent } from 'react'
import { useParams } from 'react-router-dom'
import {
  Alert,
  Avatar,
  Box,
  Button,
  Card,
  CardContent,
  Chip,
  CircularProgress,
  Container,
  MenuItem,
  Paper,
  TextField,
  Typography,
} from '@mui/material'
import PersonIcon from '@mui/icons-material/Person'
import SmartToyIcon from '@mui/icons-material/SmartToy'
import * as tutorService from '../../services/tutorService'
import type { ConversationDetail, ConversationMode, ExplanationLevel, Message } from '../../types/tutor'

function ChatPage() {
  const { conversationId } = useParams<{ conversationId: string }>()

  const [conversation, setConversation] = useState<ConversationDetail | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const [draft, setDraft] = useState('')
  const [isSending, setIsSending] = useState(false)
  const [sendError, setSendError] = useState<string | null>(null)

  const messagesEndRef = useRef<HTMLDivElement | null>(null)

  useEffect(() => {
    if (!conversationId) return
    tutorService
      .getConversation(conversationId)
      .then((data) => setConversation(data))
      .catch(() => setError('Unable to load this conversation.'))
      .finally(() => setIsLoading(false))
  }, [conversationId])

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [conversation?.messages.length])

  async function handleSend(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    if (!conversationId || !draft.trim() || !conversation) return

    const userContent = draft.trim()
    setDraft('')
    setSendError(null)

    const optimisticUserMessage: Message = {
      id: `pending-${Date.now()}`,
      role: 'user',
      content: userContent,
      sources: [],
      created_at: new Date().toISOString(),
    }
    setConversation({ ...conversation, messages: [...conversation.messages, optimisticUserMessage] })

    setIsSending(true)
    try {
      const assistantMessage = await tutorService.sendMessage(conversationId, userContent)
      setConversation((current) =>
        current ? { ...current, messages: [...current.messages, assistantMessage] } : current,
      )
    } catch {
      setSendError('The AI tutor is unavailable. Make sure Ollama is running locally, then try again.')
    } finally {
      setIsSending(false)
    }
  }

  async function handleSettingsChange(mode: ConversationMode, explanationLevel: ExplanationLevel) {
    if (!conversationId || !conversation) return
    const updated = await tutorService.updateConversation(conversationId, {
      mode,
      explanation_level: explanationLevel,
    })
    setConversation({ ...conversation, mode: updated.mode, explanation_level: updated.explanation_level })
  }

  if (isLoading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '60vh' }}>
        <CircularProgress />
      </Box>
    )
  }

  if (error || !conversation) {
    return (
      <Container maxWidth="sm">
        <Alert severity="error" sx={{ mt: 4 }}>
          {error ?? 'Conversation not found.'}
        </Alert>
      </Container>
    )
  }

  return (
    <Container maxWidth="md">
      <Box sx={{ display: 'flex', flexDirection: 'column', height: 'calc(100vh - 64px)', py: 2 }}>
        <Box
          sx={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            flexWrap: 'wrap',
            gap: 1,
            mb: 2,
          }}
        >
          <Typography variant="h5" sx={{ fontWeight: 600 }}>
            {conversation.title}
          </Typography>
          <Box sx={{ display: 'flex', gap: 1 }}>
            <TextField
              select
              size="small"
              value={conversation.explanation_level}
              onChange={(event) =>
                handleSettingsChange(conversation.mode, event.target.value as ExplanationLevel)
              }
            >
              <MenuItem value="beginner">Beginner</MenuItem>
              <MenuItem value="intermediate">Intermediate</MenuItem>
              <MenuItem value="advanced">Advanced</MenuItem>
            </TextField>
            <TextField
              select
              size="small"
              value={conversation.mode}
              onChange={(event) =>
                handleSettingsChange(event.target.value as ConversationMode, conversation.explanation_level)
              }
            >
              <MenuItem value="tutor">Direct</MenuItem>
              <MenuItem value="socratic">Socratic</MenuItem>
            </TextField>
          </Box>
        </Box>

        <Card sx={{ flexGrow: 1, overflow: 'hidden', display: 'flex', flexDirection: 'column' }}>
          <CardContent sx={{ flexGrow: 1, overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: 2 }}>
            {conversation.messages.length === 0 && (
              <Typography variant="body2" color="text.secondary">
                Ask the AI tutor a question to get started.
              </Typography>
            )}
            {conversation.messages.map((message) => (
              <Box
                key={message.id}
                sx={{
                  display: 'flex',
                  gap: 1,
                  alignSelf: message.role === 'user' ? 'flex-end' : 'flex-start',
                  flexDirection: message.role === 'user' ? 'row-reverse' : 'row',
                  maxWidth: '80%',
                }}
              >
                <Avatar
                  sx={{
                    width: 32,
                    height: 32,
                    bgcolor: message.role === 'user' ? 'primary.main' : 'secondary.main',
                  }}
                >
                  {message.role === 'user' ? <PersonIcon fontSize="small" /> : <SmartToyIcon fontSize="small" />}
                </Avatar>
                <Box
                  sx={{
                    display: 'flex',
                    flexDirection: 'column',
                    gap: 0.5,
                    alignItems: message.role === 'user' ? 'flex-end' : 'flex-start',
                  }}
                >
                  <Paper
                    variant="outlined"
                    sx={{
                      p: 1.5,
                      bgcolor: message.role === 'user' ? 'primary.main' : 'background.default',
                      color: message.role === 'user' ? 'primary.contrastText' : 'text.primary',
                    }}
                  >
                    <Typography variant="body2" sx={{ whiteSpace: 'pre-wrap' }}>
                      {message.content}
                    </Typography>
                  </Paper>
                  {message.sources.length > 0 && (
                    <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                      {message.sources.map((source) => (
                        <Chip key={source} label={source} size="small" variant="outlined" />
                      ))}
                    </Box>
                  )}
                </Box>
              </Box>
            ))}
            {isSending && (
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <CircularProgress size={16} />
                <Typography variant="body2" color="text.secondary">
                  Thinking...
                </Typography>
              </Box>
            )}
            <div ref={messagesEndRef} />
          </CardContent>
        </Card>

        {sendError && (
          <Alert severity="error" sx={{ mt: 2 }}>
            {sendError}
          </Alert>
        )}

        <Box component="form" onSubmit={handleSend} sx={{ display: 'flex', gap: 1, mt: 2 }}>
          <TextField
            value={draft}
            onChange={(event) => setDraft(event.target.value)}
            placeholder="Ask a question..."
            fullWidth
            size="small"
            disabled={isSending}
          />
          <Button type="submit" variant="contained" disabled={isSending || !draft.trim()}>
            Send
          </Button>
        </Box>
      </Box>
    </Container>
  )
}

export default ChatPage