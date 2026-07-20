import request from '@/utils/request'

// 获取系统日志
export function getSystemLogs(params) {
  return request({
    url: '/system/logs/',
    method: 'get',
    params
  })
}

// 获取系统配置
export function getSystemConfigs() {
  return request({
    url: '/system/configs/',
    method: 'get'
  })
}

// 更新系统配置
export function updateSystemConfig(id, data) {
  return request({
    url: `/system/configs/${id}/`,
    method: 'put',
    data
  })
}

// 获取系统状态
export function getSystemStatus() {
  return request({
    url: '/system/status/',
    method: 'get'
  })
} 