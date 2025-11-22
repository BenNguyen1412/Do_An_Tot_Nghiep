import { ref } from 'vue'
import { defineStore } from 'pinia'
import axiosInstance from '@/utils/axios'

interface User {
  id: number
  email: string
  full_name: string
  role: string
  phone_number?: string | null
  is_active: boolean
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

  // Initialize from localStorage
  const initAuth = () => {
    const storedToken = localStorage.getItem('token')
    const storedUser = localStorage.getItem('user')

    if (storedToken && storedUser) {
      try {
        token.value = storedToken
        user.value = JSON.parse(storedUser)
        console.log('✅ Auth initialized:', user.value)
      } catch (e) {
        console.error('❌ Failed to parse user:', e)
        logout()
      }
    }
  }

  // Signup
  const signup = async (userData: SignupData) => {
    console.log('📝 AUTH STORE - Signup called')
    console.log('   Email:', userData.email)
    console.log('   Full name:', userData.full_name)
    console.log('   Role:', userData.role)

    isLoading.value = true
    error.value = null

    try {
      console.log('📤 Sending POST request to /auth/register')

      const response = await axiosInstance.post<LoginResponse>('/auth/register', userData)

      console.log('📥 Response received:', response.status)

      if (response.data) {
        user.value = response.data.user
        token.value = response.data.access_token

        localStorage.setItem('token', token.value)
        localStorage.setItem('user', JSON.stringify(user.value))

        console.log('✅ Signup successful!')

        return { success: true, data: response.data }
      }

      return { success: false, error: 'Đăng ký thất bại' }
    } catch (err: unknown) {
      console.error('❌ Signup error:', err)

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

        console.log('   Error status:', status)
        console.log('   Error detail:', detail)

        if (status === 400 && detail?.includes('đã')) {
          errorMessage = 'Email đã được đăng ký. Vui lòng sử dụng email khác.'
        } else if (status === 422) {
          errorMessage = 'Dữ liệu không hợp lệ. Vui lòng kiểm tra lại.'
        } else if (detail) {
          errorMessage = detail
        }
      }

      error.value = errorMessage
      return { success: false, error: errorMessage }
    } finally {
      isLoading.value = false
    }
  }

  // Login
  const login = async (credentials: { email: string; password: string }) => {
    console.log('🔐 AUTH STORE - Login called')
    console.log('   Email:', credentials.email)

    isLoading.value = true
    error.value = null

    try {
      console.log('📤 Sending POST request to /auth/login')

      const response = await axiosInstance.post<LoginResponse>('/auth/login', credentials)

      console.log('📥 Response received:', response.status)

      if (response.data) {
        user.value = response.data.user
        token.value = response.data.access_token

        localStorage.setItem('token', token.value)
        localStorage.setItem('user', JSON.stringify(user.value))

        console.log('✅ Login successful!')

        return { success: true }
      }

      return { success: false, error: 'Đăng nhập thất bại' }
    } catch (err: unknown) {
      console.error('❌ Login error:', err)

      let errorMessage = 'Đăng nhập thất bại'

      if (err && typeof err === 'object' && 'response' in err) {
        const error = err as {
          response?: {
            status?: number
            data?: { detail?: string }
          }
        }

        const status = error.response?.status
        const detail = error.response?.data?.detail

        console.log('   Error status:', status)
        console.log('   Error detail:', detail)

        if (status === 401) {
          if (detail) {
            errorMessage = detail
          }
        }
      }

      error.value = errorMessage
      return { success: false, error: errorMessage }
    } finally {
      isLoading.value = false
    }
  }

  // Update Profile
  const updateProfile = async (
    userId: number,
    profileData: {
      full_name?: string
      phone_number?: string
      email?: string
      password?: string
    },
  ) => {
    console.log('✏️ AUTH STORE - Update profile called')
    console.log('   User ID:', userId)
    console.log('   Profile Data:', profileData)

    isLoading.value = true
    error.value = null

    try {
      console.log('📤 Sending PUT request to /users/' + userId)
      console.log('   Request payload:', JSON.stringify(profileData))

      const response = await axiosInstance.put<User>(`/users/${userId}`, profileData)

      console.log('📥 Response received:', response.status)
      console.log('   Response data:', response.data)

      if (response.data) {
        // Update user in store
        user.value = response.data
        localStorage.setItem('user', JSON.stringify(user.value))

        console.log('✅ Profile update successful!')

        return { success: true, data: response.data }
      }

      return { success: false, error: 'Cập nhật thất bại' }
    } catch (err: unknown) {
      console.error('❌ Update profile error:', err)

      let errorMessage = 'Cập nhật thất bại. Vui lòng thử lại.'

      if (err && typeof err === 'object' && 'response' in err) {
        const error = err as {
          response?: {
            status?: number
            data?: { detail?: string | Array<{ msg: string; type: string }> }
          }
        }

        const detail = error.response?.data?.detail
        const status = error.response?.status

        console.log('   Error status:', status)
        console.log('   Error detail:', detail)
        console.log('   Full error response:', error.response?.data)

        if (status === 404) {
          errorMessage = 'Không tìm thấy người dùng.'
        } else if (status === 400) {
          if (typeof detail === 'string' && detail.includes('Email')) {
            errorMessage = 'Email đã được sử dụng.'
          } else if (typeof detail === 'string') {
            errorMessage = detail
          } else if (Array.isArray(detail)) {
            errorMessage = detail.map((d) => d.msg).join(', ')
          }
        } else if (typeof detail === 'string') {
          errorMessage = detail
        } else if (Array.isArray(detail)) {
          errorMessage = detail.map((d) => d.msg).join(', ')
        }
      }

      error.value = errorMessage
      return { success: false, error: errorMessage }
    } finally {
      isLoading.value = false
    }
  }

  // Logout
  const logout = () => {
    console.log('🚪 Logout')
    user.value = null
    token.value = ''
    localStorage.removeItem('token')
    localStorage.removeItem('user')
  }

  // Initialize on store creation
  initAuth()

  return {
    user,
    token,
    isLoading,
    error,
    signup,
    login,
    logout,
    updateProfile,
    initAuth,
  }
})
