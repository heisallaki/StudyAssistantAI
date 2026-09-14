import { useContext } from 'react'
import { ThemeSettingsContext } from '../contexts/ThemeSettingsContext'

export function useThemeSettings() {
  const context = useContext(ThemeSettingsContext)
  if (context === undefined) {
    throw new Error('useThemeSettings must be used within a ThemeSettingsProvider')
  }
  return context
}