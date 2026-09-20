import { useEffect, useState } from 'react'
import type { ReactNode } from 'react'
import { AuthContext } from './AuthContext'
import { TOKEN_STORAGE_KEY } from '../services/api'
import * as authService from '../services/authService'
import type { AuthUser, LoginRequest, RegisterRequest } from '../types/auth'

function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(null)
  const [isLoading, setIsLoading] = useState(() => Boolean(localStorage.getItem(TOKEN_STORAGE_KEY)))

  useEffect(() => {
    if (!isLoading) {
      return
    }

    async function initializeAuth() {
      try {
        const currentUser = await authService.getCurrentUser()
        setUser(currentUser)
      } catch {
        localStorage.removeItem(TOKEN_STORAGE_KEY)
      } finally {
        setIsLoading(false)
      }
    }

    initializeAuth()
  }, [isLoading])

  async function login(credentials: LoginRequest) {
    const tokenResponse = await authService.login(credentials)
    localStorage.setItem(TOKEN_STORAGE_KEY, tokenResponse.access_token)
    const currentUser = await authService.getCurrentUser()
    setUser(currentUser)
  }

  async function register(credentials: RegisterRequest) {
    await authService.register(credentials)
    await login(credentials)
  }

  function logout() {
    localStorage.removeItem(TOKEN_STORAGE_KEY)
    setUser(null)
  }

  return (
    <AuthContext.Provider
      value={{
        user,
        isLoading,
        isAuthenticated: user !== null,
        login,
        register,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  )
}

export default AuthProvider