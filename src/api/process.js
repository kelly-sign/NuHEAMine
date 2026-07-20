import request from '@/utils/request'

// 获取工艺列表
export function getProcesses(params) {
  return request({
    url: '/processes/',
    method: 'get',
    params: {
      page: params.page || 1,
      page_size: params.page_size || 10,
      search: params.search || ''
    }
  })
}

// 创建工艺
export function createProcess(data) {
  return request({
    url: '/processes/',
    method: 'post',
    data
  })
}

// 更新工艺
export function updateProcess(id, data) {
  return request({
    url: `/processes/${id}/`,
    method: 'patch',
    data
  })
}

// 删除工艺
export function deleteProcess(id) {
  return request({
    url: `/processes/${id}/`,
    method: 'delete'
  })
}

// 导入工艺数据
export function importProcesses(data) {
  return request({
    url: '/processes/import_data/',
    method: 'post',
    headers: {
      'Content-Type': 'multipart/form-data'
    },
    data
  })
}

// 导出工艺数据
export function exportProcesses(data) {
  return request({
    url: '/processes/export_data/',
    method: 'post',
    responseType: 'blob',
    data
  })
} 