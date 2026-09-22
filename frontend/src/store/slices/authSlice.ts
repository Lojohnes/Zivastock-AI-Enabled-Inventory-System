import { createSlice, createAsyncThunk } from '@reduxjs/toolkit'
import api from '../../services/api'

interface User {
  id: number
  email: string
  first_name: string
  last_name: string
  phone_number?: string | null
  profile_picture?: string | null
  role_id: number
  permissions?: string[]
  is_active: boolean
}

interface AuthState {
  user: User | null
  token: string | null
  isAuthenticated: boolean
  loading: boolean
  error: string | null
}

const initialState: AuthState = {
  user: null,
  token: localStorage.getItem('access_token'),
  isAuthenticated: !!localStorage.getItem('access_token'),
  loading: false,
  error: null,
}

export const login = createAsyncThunk(
  'auth/login',
  async (credentials: { email: string; password: string }) => {
    const response = await api.post('/auth/login', credentials)
    return response.data
  }
)

export const register = createAsyncThunk(
  'auth/register',
  async (data: { email: string; password: string; first_name: string; last_name: string }) => {
    const response = await api.post('/auth/register', data)
    return response.data
  }
)

export const logout = createAsyncThunk('auth/logout', async () => {
  await api.post('/auth/logout')
  return null
})

const authSlice = createSlice({
  name: 'auth',
  initialState,
  reducers: {
    clearError: (state) => {
      state.error = null
    },
    setUser: (state, action) => {
      state.user = action.payload
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(login.pending, (state) => {
        state.loading = true
        state.error = null
      })
      .addCase(login.fulfilled, (state, action) => {
        state.loading = false
        state.user = action.payload.user
        state.token = action.payload.access_token
        state.isAuthenticated = true
        localStorage.setItem('access_token', action.payload.access_token)
        localStorage.setItem('refresh_token', action.payload.refresh_token)
      })
      .addCase(login.rejected, (state, action) => {
        state.loading = false
        state.error = action.error.message || 'Login failed'
      })
      .addCase(register.pending, (state) => {
        state.loading = true
        state.error = null
      })
      .addCase(register.fulfilled, (state, action) => {
        state.loading = false
        state.user = action.payload.user
        state.token = action.payload.access_token
        state.isAuthenticated = true
        localStorage.setItem('access_token', action.payload.access_token)
        localStorage.setItem('refresh_token', action.payload.refresh_token)
      })
      .addCase(register.rejected, (state, action) => {
        state.loading = false
        state.error = action.error.message || 'Registration failed'
      })
      .addCase(logout.fulfilled, (state) => {
        state.user = null
        state.token = null
        state.isAuthenticated = false
        localStorage.clear()
      })
  },
})

export const { clearError, setUser } = authSlice.actions
export default authSlice.reducer
