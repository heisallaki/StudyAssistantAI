import { useCallback, useEffect, useState } from 'react'
import type { FormEvent } from 'react'
import { Link as RouterLink, useSearchParams } from 'react-router-dom'
import {
  Alert,
  Box,
  Button,
  Card,
  CardActionArea,
  CardContent,
  Chip,
  CircularProgress,
  Container,
  Divider,
  TextField,
  Typography,
} from '@mui/material'
import AutoAwesomeIcon from '@mui/icons-material/AutoAwesome'
import SearchIcon from '@mui/icons-material/Search'
import * as searchService from '../../services/searchService'
import type { SearchResult, SearchResultType, SemanticSearchResult } from '../../types/search'

const TYPE_LABEL: Record<SearchResultType, string> = {
  subject: 'Subject',
  topic: 'Topic',
  document: 'Document',
  quiz: 'Quiz',
  flashcard_deck: 'Flashcard deck',
}

function resultLink(result: SearchResult): string {
  switch (result.result_type) {
    case 'subject':
      return `/subjects/${result.id}`
    case 'topic':
      return result.subject_id ? `/subjects/${result.subject_id}` : '/subjects'
    case 'document':
      return `/documents/${result.id}`
    case 'quiz':
      return `/quizzes/${result.id}`
    case 'flashcard_deck':
      return `/flashcards/${result.id}`
    default:
      return '/'
  }
}

function SearchPage() {
  const [searchParams, setSearchParams] = useSearchParams()
  const initialQuery = searchParams.get('q') ?? ''

  const [queryInput, setQueryInput] = useState(initialQuery)
  const [results, setResults] = useState<SearchResult[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [hasSearched, setHasSearched] = useState(false)

  const [semanticResults, setSemanticResults] = useState<SemanticSearchResult[] | null>(null)
  const [isSemanticLoading, setIsSemanticLoading] = useState(false)
  const [semanticError, setSemanticError] = useState<string | null>(null)

  const runSearch = useCallback(async (query: string) => {
    if (!query.trim()) return
    setIsLoading(true)
    setError(null)
    try {
      const response = await searchService.search(query)
      setResults(response.results)
      setHasSearched(true)
    } catch {
      setError('Unable to search right now.')
    } finally {
      setIsLoading(false)
    }
  }, [])

  useEffect(() => {
    if (!initialQuery) return
    const timeoutId = window.setTimeout(() => {
      void runSearch(initialQuery)
    }, 0)
    return () => window.clearTimeout(timeoutId)
  }, [initialQuery, runSearch])

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setSearchParams(queryInput ? { q: queryInput } : {})
    setSemanticResults(null)
    void runSearch(queryInput)
  }

  async function handleSemanticSearch() {
    if (!queryInput.trim()) return
    setIsSemanticLoading(true)
    setSemanticError(null)
    try {
      const response = await searchService.semanticSearch({ query: queryInput })
      setSemanticResults(response.results)
    } catch {
      setSemanticError('Unable to run AI search right now. Make sure your documents are indexed.')
    } finally {
      setIsSemanticLoading(false)
    }
  }

  return (
    <Container maxWidth="md">
      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3, py: 4 }}>
        <Typography variant="h4" component="h1" sx={{ fontWeight: 600 }}>
          Search
        </Typography>

        <Box component="form" onSubmit={handleSubmit} sx={{ display: 'flex', gap: 1 }}>
          <TextField
            value={queryInput}
            onChange={(event) => setQueryInput(event.target.value)}
            placeholder="Search subjects, topics, documents, quizzes, flashcards..."
            fullWidth
            autoFocus
          />
          <Button type="submit" variant="contained" startIcon={<SearchIcon />}>
            Search
          </Button>
        </Box>

        {error && <Alert severity="error">{error}</Alert>}

        {isLoading ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
            <CircularProgress />
          </Box>
        ) : hasSearched && results.length === 0 ? (
          <Card>
            <CardContent>
              <Typography variant="body2" color="text.secondary">
                No results for &quot;{searchParams.get('q')}&quot;.
              </Typography>
            </CardContent>
          </Card>
        ) : results.length > 0 ? (
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1.5 }}>
            {results.map((result) => (
              <Card key={`${result.result_type}-${result.id}`} variant="outlined">
                <CardActionArea component={RouterLink} to={resultLink(result)}>
                  <CardContent>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 0.5 }}>
                      <Chip label={TYPE_LABEL[result.result_type]} size="small" />
                      <Typography variant="subtitle1">{result.title}</Typography>
                    </Box>
                    {result.snippet && (
                      <Typography variant="body2" color="text.secondary">
                        {result.snippet}
                      </Typography>
                    )}
                  </CardContent>
                </CardActionArea>
              </Card>
            ))}
          </Box>
        ) : null}

        <Divider />

        <Box>
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
            <Box>
              <Typography variant="h6">AI-powered semantic search</Typography>
              <Typography variant="body2" color="text.secondary">
                Finds relevant passages in your uploaded documents, even without exact keyword matches.
              </Typography>
            </Box>
            <Button
              variant="outlined"
              startIcon={<AutoAwesomeIcon />}
              onClick={handleSemanticSearch}
              disabled={isSemanticLoading || !queryInput.trim()}
            >
              {isSemanticLoading ? 'Searching...' : 'Search with AI'}
            </Button>
          </Box>

          {semanticError && <Alert severity="error">{semanticError}</Alert>}

          {semanticResults &&
            (semanticResults.length === 0 ? (
              <Typography variant="body2" color="text.secondary">
                No relevant passages found in your documents.
              </Typography>
            ) : (
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1.5 }}>
                {semanticResults.map((result, index) => (
                  <Card key={index} variant="outlined">
                    <CardActionArea component={RouterLink} to={`/documents/${result.document_id}`}>
                      <CardContent>
                        <Box
                          sx={{
                            display: 'flex',
                            justifyContent: 'space-between', flexWrap: 'wrap',
                            alignItems: 'center',
                            mb: 0.5,
                          }}
                        >
                          <Typography variant="subtitle2">{result.document_title}</Typography>
                          <Chip label={`${result.similarity_percentage}% match`} size="small" color="primary" />
                        </Box>
                        <Typography variant="body2" color="text.secondary">
                          {result.chunk_text}
                        </Typography>
                      </CardContent>
                    </CardActionArea>
                  </Card>
                ))}
              </Box>
            ))}
        </Box>
      </Box>
    </Container>
  )
}

export default SearchPage