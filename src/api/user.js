import api from './index'

export const login = (data) => {
  return api.post('/auth/login/', data)
}

export const register = (data) => {
  return api.post('/auth/register/', data)
}

export const getUserInfo = () => {
  return api.get('/auth/profile/')
}

export const updateUserInfo = (data) => {
  return api.put('/auth/profile/', data)
}

export const changePassword = (data) => {
  return api.post('/auth/change-password/', data)
} 