import request from '@/utils/request'

// 获取高温力学性能列表
export function getHTProperties(params) {
  return request({
    url: '/ht-properties/',
    method: 'get',
    params: {
      page: params.page || 1,
      page_size: params.page_size || 10,
      material_id: params.material_id || '',
      process_id: params.process_id || '',
      test_type: params.test_type || '',
      // 添加范围查询参数
      htproperty_temp_min: params.htproperty_temp_min,
      htproperty_temp_max: params.htproperty_temp_max,
      yield_strength_min: params.yield_strength_min,
      yield_strength_max: params.yield_strength_max,
      ultimate_strength_min: params.ultimate_strength_min,
      ultimate_strength_max: params.ultimate_strength_max,
      fracture_strain_min: params.fracture_strain_min,
      fracture_strain_max: params.fracture_strain_max
    }
  })
}

// 创建高温力学性能记录
export function createHTProperty(data) {
  return request({
    url: '/ht-properties/',
    method: 'post',
    data
  })
}

// 更新高温力学性能记录
export function updateHTProperty(id, data) {
  return request({
    url: `/ht-properties/${id}/`,
    method: 'put',
    data
  })
}

// 删除高温力学性能记录
export function deleteHTProperty(id) {
  return request({
    url: `/ht-properties/${id}/`,
    method: 'delete'
  })
}

// 导入高温力学性能数据
export function importHTProperties(formData) {
  return request({
    url: '/ht-properties/import_data/',
    method: 'post',
    data: formData,
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

// 导出高温力学性能数据
export function exportHTProperties(data) {
  return request({
    url: '/ht-properties/export_data/',
    method: 'post',
    data,
    responseType: 'blob'
  })
} 