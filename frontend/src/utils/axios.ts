import axios from 'axios'

const instance = axios.create({
  baseURL: 'http://localhost:8000',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor
instance.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  },
)

// Response interceptor
instance.interceptors.response.use(
  (response) => {
    return response
  },
  (error) => {
    // Đảm bảo lỗi được throw đúng cách để component có thể catch
    if (error.response) {
      // Server trả về response với status code lỗi
      console.error('API Error:', error.response.data)
      return Promise.reject(error)
    } else if (error.request) {
      // Request được gửi nhưng không nhận được response
      console.error('Network Error:', error.request)
      return Promise.reject(new Error('Lỗi kết nối mạng'))
    } else {
      // Lỗi khác
      console.error('Error:', error.message)
      return Promise.reject(error)
    }
  },
)

export default instance
