import request from '@/utils/request'

/**
 * 获取蠕变测试列表
 * @param {Object} params - 查询参数
 * @returns {Promise}
 */
export function getCreTests(params) {
  return request({
    url: '/cre-tests/',
    method: 'get',
    params: {
      page: params.page || 1,
      page_size: params.page_size || 10,
      material_id: params.material_id || '',
      process_id: params.process_id || '',
      // 测试温度范围
      creep_temp_min: params.creep_temp_min,
      creep_temp_max: params.creep_temp_max,
      // 测试时间范围
      creep_time_min: params.creep_time_min,
      creep_time_max: params.creep_time_max,
      // 初始应力范围
      initial_stress_min: params.initial_stress_min,
      initial_stress_max: params.initial_stress_max,
      // 稳态蠕变速率范围
      creep_rate_min: params.creep_rate_min,
      creep_rate_max: params.creep_rate_max,
      // 蠕变极限范围
      creep_limit_min: params.creep_limit_min,
      creep_limit_max: params.creep_limit_max,
      // 蠕变持久强度范围
      creep_rupture_strength_min: params.creep_rupture_strength_min,
      creep_rupture_strength_max: params.creep_rupture_strength_max,
      // 断裂时间范围
      rupture_time_min: params.rupture_time_min,
      rupture_time_max: params.rupture_time_max,
      // 持久强度极限范围
      rupture_strength_limit_min: params.rupture_strength_limit_min,
      rupture_strength_limit_max: params.rupture_strength_limit_max,
      // 断后伸长率范围
      percentage_elongation_min: params.percentage_elongation_min,
      percentage_elongation_max: params.percentage_elongation_max
    }
  })
}

/**
 * 获取蠕变测试详情
 * @param {number} id - 蠕变测试ID
 * @returns {Promise}
 */
export function getCreTestDetail(id) {
  return request({
    url: `/cre-tests/${id}/`,
    method: 'get'
  })
}

/**
 * 创建蠕变测试记录
 * @param {Object} data - 蠕变测试数据
 * @returns {Promise}
 */
export function createCreTest(data) {
  return request({
    url: '/cre-tests/',
    method: 'post',
    data
  })
}

/**
 * 更新蠕变测试记录
 * @param {number} id - 蠕变测试ID
 * @param {Object} data - 蠕变测试数据
 * @returns {Promise}
 */
export function updateCreTest(id, data) {
  return request({
    url: `/cre-tests/${id}/`,
    method: 'put',
    data
  })
}

/**
 * 删除蠕变测试记录
 * @param {number} id - 蠕变测试ID
 * @returns {Promise}
 */
export function deleteCreTest(id) {
  return request({
    url: `/cre-tests/${id}/`,
    method: 'delete'
  })
}

/**
 * 导入蠕变测试数据
 * @param {FormData} formData - 包含Excel文件的表单数据
 * @returns {Promise}
 */
export function importCreTests(formData) {
  return request({
    url: '/cre-tests/import_data/',
    method: 'post',
    data: formData,
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

/**
 * 导出蠕变测试数据
 * @param {Object} data - 导出配置
 * @returns {Promise}
 */
export function exportCreTests(data) {
  return request({
    url: '/cre-tests/export_data/',
    method: 'post',
    data,
    responseType: 'blob'
  })
} 