import { Link as RouterLink, useLocation, useNavigate } from 'react-router-dom'
import { Box, Button, Card, CardContent, Container, Divider, Link, Typography } from '@mui/material'
import ArrowBackIcon from '@mui/icons-material/ArrowBack'
import PolicyLinks from '../../components/common/PolicyLinks'
import { CONTACT_EMAIL, LEGAL_LAST_UPDATED, OWNER_NAME, SITE_NAME } from '../../config/site'
import { LEGAL_DOCUMENTS } from '../../content/legalDocuments'
import type { LegalDocumentKey } from '../../content/legalDocuments'
import { getAccentGradient } from '../../theme/theme'

interface LegalPageProps {
  documentKey: LegalDocumentKey
}

function LegalPage({ documentKey }: LegalPageProps) {
  const navigate = useNavigate()
  const location = useLocation()
  const legalDocument = LEGAL_DOCUMENTS[documentKey]

  function handleBack() {
    if (location.key === 'default') {
      navigate('/')
      return
    }
    navigate(-1)
  }

  return (
    <Box sx={{ minHeight: '100vh', bgcolor: 'background.default', py: { xs: 2, sm: 4 } }}>
      <Container maxWidth="md">
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 1, mb: 2 }}>
          <Typography
            component={RouterLink}
            to="/"
            variant="h6"
            sx={{
              fontWeight: 800,
              letterSpacing: '-0.02em',
              background: (t) => getAccentGradient(t.palette.primary.main),
              backgroundClip: 'text',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              color: 'transparent',
              textDecoration: 'none',
              whiteSpace: 'nowrap',
            }}
          >
            {SITE_NAME}
          </Typography>
          <Button startIcon={<ArrowBackIcon />} onClick={handleBack} size="small">
            Back
          </Button>
        </Box>

        <Box component="main">
          <Card>
            <CardContent sx={{ p: { xs: 2, sm: 4 } }}>
              <Typography variant="h4" component="h1" sx={{ fontWeight: 700, mb: 0.5 }}>
                {legalDocument.title}
              </Typography>
              <Typography variant="caption" color="text.secondary" component="p" sx={{ mb: 2 }}>
                Last updated {LEGAL_LAST_UPDATED}
              </Typography>
              <Typography variant="body1" sx={{ mb: 1 }}>
                {legalDocument.intro}
              </Typography>

              {legalDocument.sections.map((section) => (
                <Box key={section.heading} component="section" sx={{ mt: 3 }}>
                  <Typography variant="h6" component="h2" sx={{ fontWeight: 600, mb: 1 }}>
                    {section.heading}
                  </Typography>
                  {section.paragraphs?.map((paragraph) => (
                    <Typography key={paragraph} variant="body1" color="text.secondary" sx={{ mb: 1.5 }}>
                      {paragraph}
                    </Typography>
                  ))}
                  {section.bullets && (
                    <Box component="ul" sx={{ pl: 3, mt: 0, mb: 0 }}>
                      {section.bullets.map((bullet) => (
                        <Typography
                          key={bullet}
                          component="li"
                          variant="body1"
                          color="text.secondary"
                          sx={{ mb: 1 }}
                        >
                          {bullet}
                        </Typography>
                      ))}
                    </Box>
                  )}
                </Box>
              ))}

              <Box component="section" sx={{ mt: 3 }}>
                <Typography variant="h6" component="h2" sx={{ fontWeight: 600, mb: 1 }}>
                  Contact
                </Typography>
                <Typography variant="body1" color="text.secondary">
                  Questions, or a request to access or delete your data? Email {OWNER_NAME} at{' '}
                  <Link href={`mailto:${CONTACT_EMAIL}`}>{CONTACT_EMAIL}</Link>.
                </Typography>
              </Box>

              <Divider sx={{ my: 3 }} />
              <Box
                sx={{
                  display: 'flex',
                  flexWrap: 'wrap',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  gap: 1,
                }}
              >
                <Typography variant="caption" color="text.secondary">
                  © {new Date().getFullYear()} {OWNER_NAME}
                </Typography>
                <PolicyLinks align="left" />
              </Box>
            </CardContent>
          </Card>
        </Box>
      </Container>
    </Box>
  )
}

export default LegalPage