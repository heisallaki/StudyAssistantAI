import { createContext } from 'react'
import type { ThemeMode } from '../theme/theme'

export interface ThemeSettingsContextValue {
  mode: ThemeMode
  accentColor: string
  setMode: (mode: ThemeMode) => void
  setAccentColor: (color: string) => void
  toggleMode: () => void
}

export const ThemeSettingsContext = createContext<ThemeSettingsContextValue | undefined>(undefined)