import axios from 'axios'
import { ElMessage } from 'element-plus'
import store from '@/store'

// 创建axios实例
const api = axios.create({
  baseURL: process.env.VUE_APP_API_URL || '/api',
  timeout: 5000
})

// 请求拦截器
api.interceptors.request.use(
  config => {
    const token = store.state.token
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`
    }
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  response => response.data,
  error => {
    const serverMessage = error.response?.data?.message
    const message = typeof serverMessage === 'string' && !/[^\u0020-\u007E]/.test(serverMessage)
      ? serverMessage
      : 'Request failed. Please try again later.'
    ElMessage.error(message)
    return Promise.reject(error)
  }
)

export default api 
