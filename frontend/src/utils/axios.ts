import axios from 'axios'

const axiosInstance = axios.create({
  baseURL: 'http://localhost:8000/api',
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor
axiosInstance.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    console.log('📤 Axios Request:', config.method?.toUpperCase(), config.url)
    return config
  },
  (error) => {
    console.error('❌ Request Error:', error)
    return Promise.reject(error)
  },
)

// Response interceptor
axiosInstance.interceptors.response.use(
  (response) => {
    console.log('📥 Axios Response:', response.status, response.config.url)
    return response
  },
  (error) => {
    console.error('❌ Axios Response Error:', error)

    // ✅ LOG CHI TIẾT ERROR
    if (error.response) {
      console.error('   Status:', error.response.status)
      console.error('   Data:', error.response.data)
      console.error('   Headers:', error.response.headers)
    } else if (error.request) {
      console.error('   No response received:', error.request)
    } else {
      console.error('   Error:', error.message)
    }
    return Promise.reject(error)
  },
)

export default axiosInstance
