import request from '@/utils/request'

/**
 * 获取辐照蠕变列表
 * @param {Object} params - 查询参数
 * @returns {Promise}
 */
export function getIrrCreeps(params) {
  return request({
    url: '/irr-creeps/',
    method: 'get',
    params: {
      page: params.page || 1,
      page_size: params.page_size || 10,
      material_id: params.material_id || '',
      process_id: params.process_id || '',
      irradiat_id: params.irradiat_id || '',
      // 实验温度范围
      ircreep_temp_min: params.ircreep_temp_min,
      ircreep_temp_max: params.ircreep_temp_max,
      // 实验时间范围
      ircreep_time_min: params.ircreep_time_min,
      ircreep_time_max: params.ircreep_time_max,
      // 初始应力范围
      irinitial_stress_min: params.irinitial_stress_min,
      irinitial_stress_max: params.irinitial_stress_max,
      // 稳态蠕变速率范围
      ircreep_rate_min: params.ircreep_rate_min,
      ircreep_rate_max: params.ircreep_rate_max,
      // 蠕变极限范围
      ircreep_limit_min: params.ircreep_limit_min,
      ircreep_limit_max: params.ircreep_limit_max,
      // 蠕变持久强度范围
      ircreep_rupture_strength_min: params.ircreep_rupture_strength_min,
      ircreep_rupture_strength_max: params.ircreep_rupture_strength_max,
      // 断裂时间范围
      irrupture_time_min: params.irrupture_time_min,
      irrupture_time_max: params.irrupture_time_max,
      // 持久强度极限范围
      irrupture_strength_limit_min: params.irrupture_strength_limit_min,
      irrupture_strength_limit_max: params.irrupture_strength_limit_max,
      // 断后伸长率范围
      irpercentage_elongation_min: params.irpercentage_elongation_min,
      irpercentage_elongation_max: params.irpercentage_elongation_max
    }
  })
}

/**
 * 获取辐照蠕变详情
 * @param {number} id - 辐照蠕变ID
 * @returns {Promise}
 */
export function getIrrCreepDetail(id) {
  return request({
    url: `/irr-creeps/${id}/`,
    method: 'get'
  })
}

/**
 * 创建辐照蠕变记录
 * @param {Object} data - 辐照蠕变数据
 * @returns {Promise}
 */
export function createIrrCreep(data) {
  return request({
    url: '/irr-creeps/',
    method: 'post',
    data
  })
}

/**
 * 更新辐照蠕变记录
 * @param {number} id - 辐照蠕变ID
 * @param {Object} data - 辐照蠕变数据
 * @returns {Promise}
 */
export function updateIrrCreep(id, data) {
  return request({
    url: `/irr-creeps/${id}/`,
    method: 'put',
    data
  })
}

/**
 * 删除辐照蠕变记录
 * @param {number} id - 辐照蠕变ID
 * @returns {Promise}
 */
export function deleteIrrCreep(id) {
  return request({
    url: `/irr-creeps/${id}/`,
    method: 'delete'
  })
}

/**
 * 导入辐照蠕变数据
 * @param {FormData} formData - 包含Excel文件的表单数据
 * @returns {Promise}
 */
export function importIrrCreeps(formData) {
  return request({
    url: '/irr-creeps/import_data/',
    method: 'post',
    data: formData,
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

/**
 * 导出辐照蠕变数据
 * @param {Object} data - 导出配置
 * @returns {Promise}
 */
export function exportIrrCreeps(data) {
  return request({
    url: '/irr-creeps/export_data/',
    method: 'post',
    data,
    responseType: 'blob'
  })
} 