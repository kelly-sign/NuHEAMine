import request from '@/utils/request'

/**
 * 获取疲劳测试列表
 * @param {Object} params - 查询参数
 * @returns {Promise}
 */
export function getFatTests(params) {
  return request({
    url: '/fat-tests/',
    method: 'get',
    params: {
      page: params.page || 1,
      page_size: params.page_size || 10,
      material_id: params.material_id || '',
      process_id: params.process_id || '',
      // 应力比范围
      stress_ratio_min: params.stress_ratio_min,
      stress_ratio_max: params.stress_ratio_max,
      // 应力幅范围
      stress_range_min: params.stress_range_min,
      stress_range_max: params.stress_range_max,
      // 平均应力范围
      mean_stress_min: params.mean_stress_min,
      mean_stress_max: params.mean_stress_max,
      // 加载频率范围
      loading_frequency_min: params.loading_frequency_min,
      loading_frequency_max: params.loading_frequency_max,
      // 环境温度范围
      environment_temp_min: params.environment_temp_min,
      environment_temp_max: params.environment_temp_max,
      // 疲劳寿命范围
      fatigue_life_min: params.fatigue_life_min,
      fatigue_life_max: params.fatigue_life_max,
      // 疲劳极限范围
      fatigue_limit_min: params.fatigue_limit_min,
      fatigue_limit_max: params.fatigue_limit_max,
      // 排序
      ordering: params.ordering || '-entry_time'
    }
  })
}

/**
 * 获取疲劳测试详情
 * @param {Number} id - 疲劳测试ID
 * @returns {Promise}
 */
export function getFatTestDetail(id) {
  return request({
    url: `/fat-tests/${id}/`,
    method: 'get'
  })
}

/**
 * 创建疲劳测试
 * @param {Object} data - 疲劳测试数据
 * @returns {Promise}
 */
export function createFatTest(data) {
  return request({
    url: '/fat-tests/',
    method: 'post',
    data
  })
}

/**
 * 更新疲劳测试
 * @param {Number} id - 疲劳测试ID
 * @param {Object} data - 更新的数据
 * @returns {Promise}
 */
export function updateFatTest(id, data) {
  return request({
    url: `/fat-tests/${id}/`,
    method: 'put',
    data,
    // 确保不对错误进行自动处理，让调用者可以捕获完整的错误信息
    validateStatus: (status) => {
      return status >= 200 && status < 300 // 只有200-299的状态码被视为成功
    }
  })
}

/**
 * 删除疲劳测试
 * @param {Number} id - 疲劳测试ID
 * @returns {Promise}
 */
export function deleteFatTest(id) {
  return request({
    url: `/fat-tests/${id}/`,
    method: 'delete'
  })
}

/**
 * 导出疲劳测试数据
 * @param {Object} data - 导出参数
 * @returns {Promise}
 */
export function exportFatTests(data) {
  return request({
    url: '/fat-tests/export_data/',
    method: 'post',
    data,
    responseType: 'blob'
  })
}

/**
 * 导入疲劳测试数据
 * @param {FormData} formData - 包含导入文件的表单数据
 * @returns {Promise}
 */
export function importFatTests(formData) {
  return request({
    url: '/fat-tests/import_data/',
    method: 'post',
    data: formData,
    headers: {
      'Content-Type': 'multipart/form-data'
    },
    timeout: 60000,
    validateStatus: (status) => {
      return status >= 200 && status < 500
    }
  })
} 