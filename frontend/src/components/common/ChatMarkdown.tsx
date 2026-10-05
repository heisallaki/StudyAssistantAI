import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { Box, Divider, Link, Typography } from '@mui/material'

interface ChatMarkdownProps {
  content: string
}

function ChatMarkdown({ content }: ChatMarkdownProps) {
  return (
    <ReactMarkdown
      remarkPlugins={[remarkGfm]}
      components={{
        p: ({ children }) => (
          <Typography
            variant="body2"
            component="p"
            sx={{ mb: 1, '&:last-child': { mb: 0 } }}
          >
            {children}
          </Typography>
        ),
        h1: ({ children }) => (
          <Typography variant="subtitle1" component="h1" sx={{ fontWeight: 700, mt: 1.5, mb: 0.5 }}>
            {children}
          </Typography>
        ),
        h2: ({ children }) => (
          <Typography variant="subtitle1" component="h2" sx={{ fontWeight: 700, mt: 1.5, mb: 0.5 }}>
            {children}
          </Typography>
        ),
        h3: ({ children }) => (
          <Typography variant="subtitle2" component="h3" sx={{ fontWeight: 700, mt: 1.5, mb: 0.5 }}>
            {children}
          </Typography>
        ),
        h4: ({ children }) => (
          <Typography variant="subtitle2" component="h4" sx={{ fontWeight: 700, mt: 1, mb: 0.5 }}>
            {children}
          </Typography>
        ),
        h5: ({ children }) => (
          <Typography variant="body2" component="h5" sx={{ fontWeight: 700, mt: 1, mb: 0.5 }}>
            {children}
          </Typography>
        ),
        h6: ({ children }) => (
          <Typography variant="body2" component="h6" sx={{ fontWeight: 700, mt: 1, mb: 0.5 }}>
            {children}
          </Typography>
        ),
        ul: ({ children }) => (
          <Box component="ul" sx={{ pl: 3, mb: 1, mt: 0 }}>
            {children}
          </Box>
        ),
        ol: ({ children }) => (
          <Box component="ol" sx={{ pl: 3, mb: 1, mt: 0 }}>
            {children}
          </Box>
        ),
        li: ({ children }) => (
          <Typography component="li" variant="body2" sx={{ mb: 0.25 }}>
            {children}
          </Typography>
        ),
        strong: ({ children }) => (
          <Box component="strong" sx={{ fontWeight: 700 }}>
            {children}
          </Box>
        ),
        em: ({ children }) => (
          <Box component="em" sx={{ fontStyle: 'italic' }}>
            {children}
          </Box>
        ),
        hr: () => <Divider sx={{ my: 1.5 }} />,
        a: ({ children, href }) => (
          <Link href={href} target="_blank" rel="noopener noreferrer">
            {children}
          </Link>
        ),
        code: ({ children }) => (
          <Box
            component="code"
            sx={{
              fontFamily: 'monospace',
              fontSize: '0.85em',
              bgcolor: 'action.hover',
              px: 0.5,
              py: 0.1,
              borderRadius: 0.5,
            }}
          >
            {children}
          </Box>
        ),
        pre: ({ children }) => (
          <Box
            component="pre"
            sx={{
              fontFamily: 'monospace',
              fontSize: '0.85em',
              bgcolor: 'action.hover',
              p: 1.5,
              borderRadius: 1,
              overflowX: 'auto',
              mb: 1,
            }}
          >
            {children}
          </Box>
        ),
        blockquote: ({ children }) => (
          <Box
            sx={{
              borderLeft: '3px solid',
              borderColor: 'divider',
              pl: 1.5,
              ml: 0,
              mb: 1,
              color: 'text.secondary',
            }}
          >
            {children}
          </Box>
        ),
        table: ({ children }) => (
          <Box sx={{ overflowX: 'auto', mb: 1 }}>
            <Box component="table" sx={{ borderCollapse: 'collapse', width: '100%' }}>
              {children}
            </Box>
          </Box>
        ),
        th: ({ children }) => (
          <Box
            component="th"
            sx={{ border: '1px solid', borderColor: 'divider', p: 0.75, textAlign: 'left', fontWeight: 700 }}
          >
            {children}
          </Box>
        ),
        td: ({ children }) => (
          <Box component="td" sx={{ border: '1px solid', borderColor: 'divider', p: 0.75 }}>
            {children}
          </Box>
        ),
      }}
    >
      {content}
    </ReactMarkdown>
  )
}

export default ChatMarkdown