import axios from 'axios';

const API_URL = `${(process.env.VUE_APP_API_URL || '/api').replace(/\/$/, '')}/`;

// 创建axios实例
const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 请求拦截器 - 添加token到请求头
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 响应拦截器 - 处理token过期
apiClient.interceptors.response.use(
  (response) => {
    return response;
  },
  async (error) => {
    const originalRequest = error.config;
    
    // 如果是401错误且不是刷新token的请求，尝试刷新token
    if (error.response?.status === 401 && !originalRequest._retry && originalRequest.url !== 'auth/refresh/') {
      originalRequest._retry = true;
      
      try {
        const refreshToken = localStorage.getItem('refresh_token');
        const response = await apiClient.post('auth/refresh/', { refresh: refreshToken });
        
        // 保存新token
        localStorage.setItem('access_token', response.data.access);
        
        // 更新请求头并重试
        originalRequest.headers.Authorization = `Bearer ${response.data.access}`;
        return apiClient(originalRequest);
      } catch (err) {
        // 刷新token失败，清除登录状态并跳转到登录页
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('user');
        window.location.href = '/login';
        return Promise.reject(err);
      }
    }
    
    return Promise.reject(error);
  }
);

export default {
  // 用户登录
  login(username, password) {
    return apiClient.post('auth/login/', { username, password });
  },
  
  // 用户注册
  register(username, password, confirmPassword) {
    return apiClient.post('auth/register/', { 
      username, 
      password, 
      confirm_password: confirmPassword 
    });
  },
  
  // 获取用户信息
  getUserProfile() {
    return apiClient.get('profile/');
  },
  
  // 刷新token
  refreshToken(refreshToken) {
    return apiClient.post('auth/refresh/', { refresh: refreshToken });
  },
  
  // 退出登录
  logout() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user');
  }
}; 
