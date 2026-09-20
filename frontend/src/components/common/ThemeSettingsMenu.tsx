import { useState } from 'react'
import type { MouseEvent } from 'react'
import { Box, IconButton, Popover, Stack, Tooltip, Typography } from '@mui/material'
import PaletteIcon from '@mui/icons-material/Palette'
import LightModeIcon from '@mui/icons-material/LightMode'
import DarkModeIcon from '@mui/icons-material/DarkMode'
import CheckIcon from '@mui/icons-material/Check'
import { useThemeSettings } from '../../hooks/useThemeSettings'
import { ACCENT_COLOR_OPTIONS } from '../../theme/theme'

function ThemeSettingsMenu() {
  const { mode, accentColor, setMode, setAccentColor } = useThemeSettings()
  const [anchorEl, setAnchorEl] = useState<HTMLElement | null>(null)

  function handleOpen(event: MouseEvent<HTMLElement>) {
    setAnchorEl(event.currentTarget)
  }

  function handleClose() {
    setAnchorEl(null)
  }

  return (
    <>
      <Tooltip title="Appearance">
        <IconButton onClick={handleOpen} color="inherit" aria-label="Appearance settings">
          <PaletteIcon />
        </IconButton>
      </Tooltip>
      <Popover
        open={Boolean(anchorEl)}
        anchorEl={anchorEl}
        onClose={handleClose}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
        transformOrigin={{ vertical: 'top', horizontal: 'right' }}
      >
        <Box sx={{ p: 2, width: 260 }}>
          <Typography variant="subtitle2" sx={{ mb: 1, fontWeight: 600 }}>
            Theme
          </Typography>
          <Stack direction="row" spacing={1} sx={{ mb: 2.5 }}>
            <IconButton
              onClick={() => setMode('light')}
              color={mode === 'light' ? 'primary' : 'default'}
              aria-label="Light mode"
              sx={{
                border: '1px solid',
                borderColor: mode === 'light' ? 'primary.main' : 'divider',
              }}
            >
              <LightModeIcon fontSize="small" />
            </IconButton>
            <IconButton
              onClick={() => setMode('dark')}
              color={mode === 'dark' ? 'primary' : 'default'}
              aria-label="Dark mode"
              sx={{
                border: '1px solid',
                borderColor: mode === 'dark' ? 'primary.main' : 'divider',
              }}
            >
              <DarkModeIcon fontSize="small" />
            </IconButton>
          </Stack>

          <Typography variant="subtitle2" sx={{ mb: 1, fontWeight: 600 }}>
            Accent colour
          </Typography>
          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1.25 }}>
            {ACCENT_COLOR_OPTIONS.map((option) => (
              <Tooltip key={option.value} title={option.name}>
                <Box
                  component="button"
                  type="button"
                  onClick={() => setAccentColor(option.value)}
                  aria-label={`Use ${option.name} accent colour`}
                  sx={{
                    width: 32,
                    height: 32,
                    borderRadius: '50%',
                    bgcolor: option.value,
                    border: '2px solid',
                    borderColor: accentColor === option.value ? 'text.primary' : 'transparent',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    cursor: 'pointer',
                    p: 0,
                    transition: 'transform 0.15s ease',
                    '&:hover': {
                      transform: 'scale(1.1)',
                    },
                  }}
                >
                  {accentColor === option.value && (
                    <CheckIcon sx={{ fontSize: 16, color: '#fff' }} />
                  )}
                </Box>
              </Tooltip>
            ))}
          </Box>
        </Box>
      </Popover>
    </>
  )
}

export default ThemeSettingsMenu