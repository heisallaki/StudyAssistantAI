import { BrowserRouter } from 'react-router-dom'
import ThemeSettingsProvider from './contexts/ThemeSettingsProvider'
import AuthProvider from './contexts/AuthProvider'
import AppRoutes from './routes/AppRoutes'

function App() {
  return (
    <ThemeSettingsProvider>
      <BrowserRouter>
        <AuthProvider>
          <AppRoutes />
        </AuthProvider>
      </BrowserRouter>
    </ThemeSettingsProvider>
  )
}

export default App