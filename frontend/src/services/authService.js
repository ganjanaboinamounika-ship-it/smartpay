
import api, { TOKEN_STORAGE_KEY } from './api'

// 1. Register a new user
export async function registerUser(credentials) {
  const response = await api.post('/auth/register', credentials)
  return response.data
}

// 2. Login and save JWT access token
export async function loginUser(credentials) {
  const response = await api.post('/auth/login', credentials)

  const { access_token } = response.data

  if (access_token) {
    localStorage.setItem(TOKEN_STORAGE_KEY, access_token)
  }

  return response.data
}

// 3. Get the currently authenticated user
export async function getCurrentUser() {
  const response = await api.get('/auth/me')
  return response.data
}

// 4. Logout by removing the locally stored token
export function logoutUser() {
  localStorage.removeItem(TOKEN_STORAGE_KEY)
}

// 5. Check whether a token exists
export function isAuthenticated() {
  return Boolean(localStorage.getItem(TOKEN_STORAGE_KEY))
}
