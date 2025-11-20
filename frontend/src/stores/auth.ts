import { ref } from 'vue'
import { defineStore } from 'pinia'
import axiosInstance from '@/utils/axios'

interface User {
  id: number
  email: string
  full_name: string
  role: string
  phone_number?: string
}

interface LoginResponse {
  access_token: string
  token_type: string
  user: User
}

interface SignupData {
  email: string
  password: string
  full_name: string
  phone_number?: string
  role: string
}

export const useAuthStore = defineStore('auth', () => {
  const user = ref<User | null>(null)
  const token = ref<string>('')
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  // Initialize auth from localStorage
  const initAuth = () => {
    const storedToken = localStorage.getItem('token')
    const storedUser = localStorage.getItem('user')

    if (storedToken && storedUser) {
      try {
        token.value = storedToken
        user.value = JSON.parse(storedUser)
        console.log('✅ Auth initialized from storage:', user.value)
      } catch (e) {
        console.error('❌ Failed to parse stored user:', e)
        logout()
      }
    }
  }

  // Check if user is authenticated
  const checkAuth = (): boolean => {
    const storedToken = localStorage.getItem('token')
    const storedUser = localStorage.getItem('user')

    if (storedToken && storedUser) {
      try {
        if (!user.value) {
          token.value = storedToken
          user.value = JSON.parse(storedUser)
        }
        return true
      } catch (e) {
        console.error('❌ Failed to parse stored user:', e)
        logout()
        return false
      }
    }

    return false
  }

  // Signup function
  const signup = async (userData: SignupData) => {
    console.log('🔵 AUTH STORE: signup called with:', userData)
    isLoading.value = true
    error.value = null

    try {
      console.log('🔵 AUTH STORE: Sending request to /auth/register')

      const response = await axiosInstance.post<LoginResponse>('/auth/register', userData)

      console.log('🔵 AUTH STORE: Response received:', response.data)

      if (response.data) {
        user.value = response.data.user
        token.value = response.data.access_token

        localStorage.setItem('token', token.value)
        localStorage.setItem('user', JSON.stringify(user.value))

        console.log('✅ AUTH STORE: Signup successful')
        return { success: true, data: response.data }
      }

      return { success: false, error: 'Đăng ký thất bại' }
    } catch (err: unknown) {
      console.error('❌ AUTH STORE: Signup error:', err)

      let errorMessage = 'Đăng ký thất bại. Vui lòng thử lại.'

      if (err && typeof err === 'object' && 'response' in err) {
        const error = err as {
          response?: {
            status?: number
            data?: { detail?: string }
          }
        }

        const detail = error.response?.data?.detail
        const status = error.response?.status

        if (status === 400 && detail?.includes('đã tồn tại')) {
          errorMessage = 'Email đã được đăng ký. Vui lòng sử dụng email khác.'
        } else if (detail) {
          errorMessage = detail
        }
      }

      error.value = errorMessage
      console.log('❌ AUTH STORE: Error message:', errorMessage)
      return { success: false, error: errorMessage }
    } finally {
      isLoading.value = false
      console.log('🔵 AUTH STORE: isLoading set to false')
    }
  }

  // Login function
  const login = async (credentials: { email: string; password: string }) => {
    console.log('🔐 AUTH STORE: login called for:', credentials.email)
    isLoading.value = true
    error.value = null

    try {
      console.log('🔐 AUTH STORE: Sending request to /auth/login')

      const response = await axiosInstance.post<LoginResponse>('/auth/login', credentials)

      console.log('✅ AUTH STORE: Login successful:', response.data)

      if (response.data) {
        user.value = response.data.user
        token.value = response.data.access_token

        localStorage.setItem('token', token.value)
        localStorage.setItem('user', JSON.stringify(user.value))

        return { success: true }
      }

      return { success: false, error: 'Đăng nhập thất bại' }
    } catch (err: unknown) {
      console.error('❌ AUTH STORE: Login error:', err)

      let errorMessage = 'Đăng nhập thất bại'

      if (err && typeof err === 'object' && 'response' in err) {
        const error = err as {
          response?: {
            status?: number
            data?: { detail?: string }
          }
          message?: string
        }

        const status = error.response?.status
        const detail = error.response?.data?.detail

        if (status === 401) {
          if (detail?.includes('không tồn tại') || detail?.includes('User không tồn tại')) {
            errorMessage = 'Email không tồn tại trong hệ thống'
          } else if (detail?.includes('mật khẩu') || detail?.includes('password')) {
            errorMessage = 'Mật khẩu không chính xác'
          } else {
            errorMessage = 'Email hoặc mật khẩu không đúng'
          }
        } else if (status === 404) {
          errorMessage = 'Email không tồn tại trong hệ thống'
        } else if (status === 422) {
          errorMessage = 'Dữ liệu đăng nhập không hợp lệ'
        } else if (status === 500) {
          errorMessage = 'Lỗi server. Vui lòng thử lại sau.'
        } else if (detail) {
          errorMessage = detail
        } else if (error.message) {
          errorMessage = error.message
        }
      } else if (err instanceof Error) {
        errorMessage = err.message
      }

      error.value = errorMessage
      return { success: false, error: errorMessage }
    } finally {
      isLoading.value = false
    }
  }

  // Logout function
  const logout = () => {
    console.log('🚪 AUTH STORE: Logging out')
    user.value = null
    token.value = ''
    localStorage.removeItem('token')
    localStorage.removeItem('user')
  }

  // Initialize on store creation
  initAuth()

  return {
    // State
    user,
    token,
    isLoading,
    error,
    // Actions
    signup,
    login,
    logout,
    checkAuth,
    initAuth,
  }
})
