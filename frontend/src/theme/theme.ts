import { alpha, createTheme, darken } from '@mui/material/styles'
import type { Theme } from '@mui/material/styles'

export type ThemeMode = 'light' | 'dark'

export interface AccentColorOption {
  name: string
  value: string
}

export const ACCENT_COLOR_OPTIONS: AccentColorOption[] = [
  { name: 'Blue', value: '#2454FF' },
  { name: 'Indigo', value: '#4F46E5' },
  { name: 'Purple', value: '#7C3AED' },
  { name: 'Pink', value: '#DB2777' },
  { name: 'Red', value: '#E11D48' },
  { name: 'Orange', value: '#F97316' },
  { name: 'Green', value: '#00B894' },
  { name: 'Teal', value: '#0D9488' },
]

export const DEFAULT_ACCENT_COLOR = ACCENT_COLOR_OPTIONS[0].value
export const DEFAULT_THEME_MODE: ThemeMode = 'light'

export function buildTheme(mode: ThemeMode, accentColor: string): Theme {
  const isDark = mode === 'dark'

  return createTheme({
    palette: {
      mode,
      primary: {
        main: accentColor,
      },
      secondary: {
        main: '#00B894',
      },
      background: {
        default: isDark ? '#0B0F19' : '#F5F7FB',
        paper: isDark ? '#141B2D' : '#FFFFFF',
      },
    },
    typography: {
      fontFamily: ['Inter', 'Roboto', 'Helvetica', 'Arial', 'sans-serif'].join(','),
    },
    shape: {
      borderRadius: 10,
    },
  })
}

export function getAccentGradient(accentColor: string): string {
  return `linear-gradient(135deg, ${accentColor} 0%, ${darken(accentColor, 0.3)} 100%)`
}

export function getGlassBackground(theme: Theme): string {
  return alpha(theme.palette.background.paper, theme.palette.mode === 'dark' ? 0.6 : 0.75)
}

export function getGlassShadow(theme: Theme): string {
  return theme.palette.mode === 'dark'
    ? '0 8px 32px rgba(0, 0, 0, 0.45)'
    : '0 8px 32px rgba(15, 23, 42, 0.08)'
}