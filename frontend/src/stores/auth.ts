import { ref } from 'vue'
import { defineStore } from 'pinia'
import axiosInstance from '@/utils/axios'

export const useAuthStore = defineStore('auth', () => {
  const user = ref<any>(null)
  const token = ref(localStorage.getItem('token') || '')
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  const signup = async (userData: {
    email: string
    password: string
    full_name: string
    phone_number?: string
    role: string
  }) => {
    isLoading.value = true
    error.value = null

    try {
      console.log('Sending signup request with data:', userData)

      // Gọi API register
      const response = await axiosInstance.post('/auth/register', userData)

      console.log('Signup response:', response.data)

      if (response.data) {
        user.value = response.data.user || response.data
        token.value = response.data.access_token || ''

        if (token.value) {
          localStorage.setItem('token', token.value)
          localStorage.setItem('user', JSON.stringify(user.value))
        }

        return { success: true, data: response.data }
      }
    } catch (err: any) {
      console.error('Signup error:', err)
      console.error('Error response:', err.response)

      const errorMessage = err.response?.data?.detail || 'Đăng ký thất bại. Vui lòng thử lại.'
      error.value = errorMessage

      return { success: false, error: errorMessage }
    } finally {
      isLoading.value = false
    }
  }

  const login = async (credentials: { email: string; password: string }) => {
    isLoading.value = true
    error.value = null

    try {
      console.log('Sending login request')

      const response = await axiosInstance.post('/auth/login', credentials)

      console.log('Login response:', response.data)

      if (response.data) {
        user.value = response.data.user
        token.value = response.data.access_token

        localStorage.setItem('token', token.value)
        localStorage.setItem('user', JSON.stringify(user.value))

        return { success: true }
      }
    } catch (err: any) {
      console.error('Login error:', err)

      const errorMessage = err.response?.data?.detail || 'Đăng nhập thất bại'
      error.value = errorMessage

      return { success: false, error: errorMessage }
    } finally {
      isLoading.value = false
    }
  }

  const logout = () => {
    user.value = null
    token.value = ''
    localStorage.removeItem('token')
    localStorage.removeItem('user')
  }

  const checkAuth = () => {
    const storedToken = localStorage.getItem('token')
    const storedUser = localStorage.getItem('user')

    if (storedToken && storedUser) {
      token.value = storedToken
      user.value = JSON.parse(storedUser)
      return true
    }
    return false
  }

  return {
    user,
    token,
    isLoading,
    error,
    signup,
    login,
    logout,
    checkAuth,
  }
})
