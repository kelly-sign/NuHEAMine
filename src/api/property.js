import request from '@/utils/request'

// 获取室温结构性能列表
export function getRoomTempProperties(params) {
  return request({
    url: '/room-temp-properties/',
    method: 'get',
    params: {
      ...params,
      // 确保相结构搜索参数正确传递
      search: params.phase_structure,
    }
  })
}

// 创建室温结构性能记录
export function createRoomTempProperty(data) {
  return request({
    url: '/room-temp-properties/',
    method: 'post',
    data
  })
}

// 更新室温结构性能记录
export function updateRoomTempProperty(id, data) {
  return request({
    url: `/room-temp-properties/${id}/`,
    method: 'put',
    data
  })
}

// 删除室温结构性能记录
export function deleteRoomTempProperty(id) {
  return request({
    url: `/room-temp-properties/${id}/`,
    method: 'delete'
  })
}

// 导出室温结构性能数据
export function exportRoomTempProperties(data) {
  return request({
    url: '/room-temp-properties/export_data/',
    method: 'post',
    data,
    responseType: 'blob'
  })
} 
