import request from '@/utils/request'

// 获取材料列表
export function getMaterials(params) {
  return request({
    url: '/materials/',
    method: 'get',
    params
  })
}

// 获取材料详情
export function getMaterialDetail(id) {
  return request({
    url: `/materials/${id}/`,
    method: 'get'
  })
}

// 创建材料
export function createMaterial(data) {
  return request({
    url: '/materials/',
    method: 'post',
    data
  })
}

// 更新材料
export function updateMaterial(id, data) {
  return request({
    url: `/materials/${id}/`,
    method: 'put',
    data
  })
}

// 删除材料
export function deleteMaterial(id) {
  return request({
    url: `/materials/${id}/`,
    method: 'delete'
  })
}

// 批量删除材料
export function batchDeleteMaterials(ids) {
  return request({
    url: '/materials/batch_delete/',
    method: 'post',
    data: { ids }
  })
}

// 导入材料数据
export function importMaterials(data) {
  return request({
    url: '/materials/import_data/',
    method: 'post',
    data,
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

// 导出材料数据
export function exportData(data) {
  return request({
    url: '/materials/export_data/',
    method: 'post',
    data,
    responseType: 'blob'
  })
}

// 高级搜索
export function advancedSearch(data) {
  return request({
    url: '/materials/advanced_search/',
    method: 'post',
    data
  })
}

// 获取数据统计
export function getMaterialStatistics() {
  return request({
    url: '/materials/statistics/',
    method: 'get'
  })
}

// 获取材料类型列表
export function getMaterialTypes() {
  return request({
    url: '/materials/types/',
    method: 'get'
  })
}

// 获取性能指标列表
export function getPropertyNames() {
  return request({
    url: '/materials/property_names/',
    method: 'get'
  })
}