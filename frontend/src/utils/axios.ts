import axios from 'axios'

const axiosInstance = axios.create({
  baseURL: 'http://localhost:8000/api',
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000,
})

// Request interceptor
axiosInstance.interceptors.request.use(
  (config) => {
    console.log('📤 AXIOS REQUEST:')
    console.log('   Method:', config.method?.toUpperCase())
    console.log('   Full URL:', config.baseURL + config.url)
    console.log('   Data:', config.data)

    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }

    return config
  },
  (error) => {
    console.error('❌ AXIOS REQUEST ERROR:', error)
    return Promise.reject(error)
  },
)

// Response interceptor
axiosInstance.interceptors.response.use(
  (response) => {
    console.log('📥 AXIOS RESPONSE:')
    console.log('   Status:', response.status)
    console.log('   Data:', response.data)
    return response
  },
  (error) => {
    console.error('❌ AXIOS RESPONSE ERROR:')
    console.error('   Status:', error.response?.status)
    console.error('   URL:', error.config?.baseURL + error.config?.url)
    console.error('   Data:', error.response?.data)

    return Promise.reject(error)
  },
)

export default axiosInstance
