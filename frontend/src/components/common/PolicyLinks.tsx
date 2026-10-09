import { Link as RouterLink } from 'react-router-dom'
import { Box, Link } from '@mui/material'

const POLICY_LINKS = [
  { to: '/privacy', label: 'Privacy' },
  { to: '/terms', label: 'Terms' },
  { to: '/disclaimer', label: 'AI disclaimer' },
]

interface PolicyLinksProps {
  align?: 'left' | 'center'
}

function PolicyLinks({ align = 'center' }: PolicyLinksProps) {
  return (
    <Box
      component="nav"
      aria-label="Legal"
      sx={{
        display: 'flex',
        flexWrap: 'wrap',
        justifyContent: align === 'center' ? 'center' : 'flex-start',
        columnGap: 2,
        rowGap: 0.5,
      }}
    >
      {POLICY_LINKS.map((link) => (
        <Link
          key={link.to}
          component={RouterLink}
          to={link.to}
          variant="caption"
          color="text.secondary"
          underline="hover"
        >
          {link.label}
        </Link>
      ))}
    </Box>
  )
}

export default PolicyLinks