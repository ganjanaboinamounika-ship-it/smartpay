
import {
  createContext,
  useContext,
  useEffect,
  useState,
} from 'react'

import {
  loginUser,
  registerUser,
  getCurrentUser,
  logoutUser,
  isAuthenticated as hasToken,
} from '../services/authService'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  // Restore the logged-in user when the application opens
  useEffect(() => {
    let isMounted = true

    async function loadUser() {
      if (!hasToken()) {
        if (isMounted) setLoading(false)
        return
      }

      try {
        const currentUser = await getCurrentUser()

        if (isMounted) {
          setUser(currentUser)
        }
      } catch {
        logoutUser()

        if (isMounted) {
          setUser(null)
        }
      } finally {
        if (isMounted) {
          setLoading(false)
        }
      }
    }

    loadUser()

    return () => {
      isMounted = false
    }
  }, [])

  // Login
  async function login(credentials) {
    const response = await loginUser(credentials)
    setUser(response.user)
    return response
  }

  // Register
  async function register(credentials) {
    return await registerUser(credentials)
  }

  // Logout
  function logout() {
    logoutUser()
    setUser(null)
  }

  const value = {
    user,
    loading,
    isAuthenticated: Boolean(user),
    login,
    register,
    logout,
  }

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  )
}

// eslint-disable-next-line react-refresh/only-export-components
export function useAuth() {
  const context = useContext(AuthContext)

  if (!context) {
    throw new Error('useAuth must be used inside AuthProvider')
  }

  return context
}
