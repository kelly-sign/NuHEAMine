import axios from 'axios'
import { ElMessage } from 'element-plus'
import { getToken, getRefreshToken } from '@/utils/auth'
import router from '@/router'
import store from '@/store'

// 是否正在刷新token
let isRefreshing = false
// 重试队列，每一项将是一个待执行的函数形式
let retryRequests = []

const fallbackMessages = {
  400: 'Invalid request parameters',
  401: 'Session expired, please log in again',
  403: 'You do not have permission to access this resource',
  404: 'The requested resource was not found'
}

const getFallbackMessage = (status) => {
  return fallbackMessages[status] || 'Request failed. Please try again later.'
}

const getEnglishDisplayMessage = (message, status) => {
  const normalized = typeof message === 'string' ? message.trim() : ''
  const isPrintableAscii = Array.from(normalized).every(character => {
    const codePoint = character.codePointAt(0)
    return codePoint >= 32 && codePoint <= 126
  })
  return normalized && isPrintableAscii
    ? normalized
    : getFallbackMessage(status)
}

// 创建axios实例
const service = axios.create({
  baseURL: process.env.VUE_APP_API_URL,
  timeout: 15000
})

// 请求拦截器
service.interceptors.request.use(
  config => {
    const token = getToken()
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`
      return config
    }
    
    // 如果请求的是登录、注册或刷新token接口，不需要token
    const whiteList = ['/auth/login/', '/auth/register/', '/auth/refresh/']
    if (whiteList.includes(config.url)) {
      return config
    }
    
    // 其他情况，Cancel请求并重定向到登录页
    ElMessage({
      message: 'Please log in first',
      type: 'warning',
      duration: 3 * 1000
    })
    router.push('/login')
    return Promise.reject(new Error('Please log in first'))
  },
  error => {
    return Promise.reject(error)
  }
)

// 响应拦截器
service.interceptors.response.use(
  response => {
    // 如果是blobType（文件下载），直接返回
    if (response.config.responseType === 'blob') {
      // 检查是否有错误响应
      if (response.data.type && response.data.type.includes('application/json')) {
        // 可能是一个JSON错误响应
        return new Promise((resolve, reject) => {
          const reader = new FileReader()
          reader.onload = () => {
            try {
              const errorData = JSON.parse(reader.result)
              reject(new Error(getEnglishDisplayMessage(errorData.detail, response.status) || 'Export failed'))
            } catch (e) {
              reject(new Error('Invalid response format'))
            }
          }
          reader.onerror = () => reject(new Error('Unable to read response data'))
          reader.readAsText(response.data)
        })
      }
      return response
    }

    // 返回响应数据
    return response
  },
  async error => {
    console.error('Response error:')
    
    // 如果请求配置中设置了自定义的validateStatus，则不进行默认处理
    if (error.config && error.config.validateStatus && !error.config.validateStatus(error.response?.status)) {
      // 将错误返回给调用者处理
      return Promise.reject(error)
    }
    
    // 提取响应状态码
    const status = error.response ? error.response.status : null
    // 原始请求配置
    const originalRequest = error.config
    
    // 处理401错误 - token过期
    if (status === 401 && !originalRequest._retry) {
      // 如果已经标记为重试，则不再尝试刷新token
      if (originalRequest._retry) {
        return Promise.reject(error)
      }
      
      // 如果正在刷新token，则将请求Add到重试队列
      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          retryRequests.push(() => {
            originalRequest.headers['Authorization'] = 'Bearer ' + getToken()
            resolve(service(originalRequest))
          })
        })
      }
      
      // 标记原始请求为重试
      originalRequest._retry = true
      isRefreshing = true
      
      try {
        // 获取refresh_token
        const refreshToken = getRefreshToken()
        if (!refreshToken) {
          throw new Error('No refresh token available')
        }
        
        // 尝试刷新token
        await store.dispatch('user/refreshToken')
        
        // 更新请求头的Authorization
        originalRequest.headers['Authorization'] = 'Bearer ' + getToken()
        
        // 执行队列中的所有请求
        retryRequests.forEach(callback => callback())
        retryRequests = []
        
        // 返回原始请求
        return service(originalRequest)
      } catch (refreshError) {
        console.error('Token refresh failed:')
        // 刷新失败，清除User状态并跳转到登录页
        store.dispatch('user/logout')
        router.push('/login')
        
        // 显示友好Confirm
        ElMessage({
          message: 'Session expired, please log in again',
          type: 'warning',
          duration: 3 * 1000
        })
        
        return Promise.reject(refreshError)
      } finally {
        isRefreshing = false
      }
    }
    
    let errorMsg = ''
    
    if (error.response) {
      switch (error.response.status) {
        case 401:
          // 401错误已在上面特殊处理
          errorMsg = 'Session expired, please log in again'
          break
        case 403:
          errorMsg = 'You do not have permission to access this resource'
          break
        case 404:
          errorMsg = 'The requested resource was not found'
          break
        case 400:
          // 尝试获取详细的验证错误
          if (typeof error.response.data === 'object') {
            // Format error信息
            const errMsgs = []
            for (const key in error.response.data) {
              if (Array.isArray(error.response.data[key])) {
                errMsgs.push(`${key}: ${error.response.data[key].join(', ')}`)
              } else if (typeof error.response.data[key] === 'string') {
                errMsgs.push(`${key}: ${error.response.data[key]}`)
              }
            }
            if (errMsgs.length > 0) {
              errorMsg = errMsgs.join('; ')
            } else {
              errorMsg = 'Invalid request parameters'
            }
          } else {
            errorMsg = error.response.data?.error || error.response.data?.message || error.response.data || 'Invalid request parameters'
          }
          break
        default:
          errorMsg = error.response.data?.error || error.response.data?.message || 'Request failed. Please try again later.'
      }
    } else if (error.message === 'Invalid response format') {
      errorMsg = 'Invalid server response format'
    } else {
      errorMsg = 'Network error, please check your connection'
    }

    errorMsg = getEnglishDisplayMessage(errorMsg, status)

    // 不是401错误才显示Confirm，避免重复Confirm
    if (status !== 401) {
    ElMessage({
      message: errorMsg,
      type: 'error',
      duration: 5 * 1000
    })
    }
    
    return Promise.reject(error)
  }
)

export default service 
