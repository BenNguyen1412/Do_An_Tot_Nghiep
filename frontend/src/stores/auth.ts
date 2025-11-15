import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import axios from '@/utils/axios'
import { useRouter } from 'vue-router'

interface User {
  id: number
  email: string
  full_name: string
  role: 'user' | 'enterprise' | 'owner'
  phone_number?: string
  address?: string
  avatar_url?: string
}

interface LoginCredentials {
  email: string
  password: string
  role: 'user' | 'enterprise' | 'owner'
}

interface SignupData {
  email: string
  password: string
  full_name: string
  role: 'user' | 'enterprise' | 'owner'
  phone_number?: string
}

export const useAuthStore = defineStore('auth', () => {
  const user = ref<User | null>(null)
  const accessToken = ref<string | null>(null)
  const refreshToken = ref<string | null>(null)
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  const isAuthenticated = computed(() => !!accessToken.value && !!user.value)
  const userRole = computed(() => user.value?.role)

  // Khởi tạo từ localStorage
  const initAuth = () => {
    const savedUser = localStorage.getItem('user')
    const savedAccessToken = localStorage.getItem('access_token')
    const savedRefreshToken = localStorage.getItem('refresh_token')

    if (savedUser && savedAccessToken) {
      user.value = JSON.parse(savedUser)
      accessToken.value = savedAccessToken
      refreshToken.value = savedRefreshToken
    }
  }

  // Đăng ký
  const signup = async (data: SignupData) => {
    isLoading.value = true
    error.value = null

    try {
      const response = await axios.post('/auth/signup', data)

      const { user: userData, access_token, refresh_token } = response.data

      // Lưu vào state
      user.value = userData
      accessToken.value = access_token
      refreshToken.value = refresh_token

      // Lưu vào localStorage
      localStorage.setItem('user', JSON.stringify(userData))
      localStorage.setItem('access_token', access_token)
      localStorage.setItem('refresh_token', refresh_token)

      return { success: true, data: response.data }
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Đăng ký thất bại'
      return { success: false, error: error.value }
    } finally {
      isLoading.value = false
    }
  }

  // Đăng nhập
  const login = async (credentials: LoginCredentials) => {
    isLoading.value = true
    error.value = null

    try {
      const response = await axios.post('/auth/login', credentials)

      const { user: userData, access_token, refresh_token } = response.data

      // Lưu vào state
      user.value = userData
      accessToken.value = access_token
      refreshToken.value = refresh_token

      // Lưu vào localStorage
      localStorage.setItem('user', JSON.stringify(userData))
      localStorage.setItem('access_token', access_token)
      localStorage.setItem('refresh_token', refresh_token)

      return { success: true, data: response.data }
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Đăng nhập thất bại'
      return { success: false, error: error.value }
    } finally {
      isLoading.value = false
    }
  }

  // Đăng xuất
  const logout = async () => {
    try {
      await axios.post('/auth/logout')
    } catch (err) {
      console.error('Logout error:', err)
    } finally {
      // Clear state
      user.value = null
      accessToken.value = null
      refreshToken.value = null

      // Clear localStorage
      localStorage.removeItem('user')
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
    }
  }

  // Lấy thông tin user hiện tại
  const getCurrentUser = async () => {
    if (!accessToken.value) return

    try {
      const response = await axios.get('/auth/me')
      user.value = response.data
      localStorage.setItem('user', JSON.stringify(response.data))
    } catch (err) {
      console.error('Get current user error:', err)
      logout()
    }
  }

  // Cập nhật profile
  const updateProfile = async (data: Partial<User>) => {
    isLoading.value = true
    error.value = null

    try {
      const response = await axios.put('/auth/profile', data)
      user.value = response.data
      localStorage.setItem('user', JSON.stringify(response.data))

      return { success: true, data: response.data }
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Cập nhật thất bại'
      return { success: false, error: error.value }
    } finally {
      isLoading.value = false
    }
  }

  return {
    user,
    accessToken,
    isAuthenticated,
    userRole,
    isLoading,
    error,
    initAuth,
    signup,
    login,
    logout,
    getCurrentUser,
    updateProfile,
  }
})
