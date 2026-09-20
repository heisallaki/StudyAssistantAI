import { useMemo, useState } from 'react'
import type { ReactNode } from 'react'
import { CssBaseline, ThemeProvider } from '@mui/material'
import { ThemeSettingsContext } from './ThemeSettingsContext'
import { buildTheme, DEFAULT_ACCENT_COLOR, DEFAULT_THEME_MODE } from '../theme/theme'
import type { ThemeMode } from '../theme/theme'

const MODE_STORAGE_KEY = 'studyassistant_theme_mode'
const ACCENT_STORAGE_KEY = 'studyassistant_accent_color'
const HEX_COLOR_PATTERN = /^#[0-9A-Fa-f]{6}$/

function readStoredMode(): ThemeMode {
  const stored = localStorage.getItem(MODE_STORAGE_KEY)
  return stored === 'dark' || stored === 'light' ? stored : DEFAULT_THEME_MODE
}

function readStoredAccentColor(): string {
  const stored = localStorage.getItem(ACCENT_STORAGE_KEY)
  return stored && HEX_COLOR_PATTERN.test(stored) ? stored : DEFAULT_ACCENT_COLOR
}

function ThemeSettingsProvider({ children }: { children: ReactNode }) {
  const [mode, setModeState] = useState<ThemeMode>(readStoredMode)
  const [accentColor, setAccentColorState] = useState<string>(readStoredAccentColor)

  function setMode(nextMode: ThemeMode) {
    setModeState(nextMode)
    localStorage.setItem(MODE_STORAGE_KEY, nextMode)
  }

  function setAccentColor(nextColor: string) {
    setAccentColorState(nextColor)
    localStorage.setItem(ACCENT_STORAGE_KEY, nextColor)
  }

  function toggleMode() {
    setMode(mode === 'light' ? 'dark' : 'light')
  }

  const theme = useMemo(() => buildTheme(mode, accentColor), [mode, accentColor])

  return (
    <ThemeSettingsContext.Provider value={{ mode, accentColor, setMode, setAccentColor, toggleMode }}>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        {children}
      </ThemeProvider>
    </ThemeSettingsContext.Provider>
  )
}

export default ThemeSettingsProvider