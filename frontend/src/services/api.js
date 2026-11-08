
import axios from 'axios'

// Token key shared by the authentication system.
export const TOKEN_STORAGE_KEY = 'smartpay_access_token'

// Backend API configuration.
const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000'

// Create one reusable Axios instance.
const api = axios.create({
  baseURL: `${API_BASE_URL}/api/v1`,
  timeout: 15000,
  headers: {
    'Content-Type': 'application/json',
    Accept: 'application/json',
  },
})

// Attach the JWT token automatically when available.
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem(TOKEN_STORAGE_KEY)

    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }

    return config
  },
  (error) => Promise.reject(error),
)

// Centralized response error handling.
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response) {
      console.error(
        'API Error:',
        error.response.status,
        error.response.data,
      )
    } else if (error.request) {
      console.error('API is not reachable:', error.message)
    } else {
      console.error('Request setup error:', error.message)
    }

    return Promise.reject(error)
  },
)

export default api
