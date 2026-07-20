import request from '@/utils/request'

/**
 * 获取辐照脆化列表
 * @param {Object} params - 查询参数
 * @returns {Promise}
 */
export function getEmbrittlementList(params) {
  return request({
    url: '/embrittlements/',
    method: 'get',
    params
  })
}

/**
 * 获取辐照脆化详情
 * @param {Number} id - 辐照脆化ID
 * @returns {Promise}
 */
export function getEmbrittlementDetail(id) {
  return request({
    url: `/embrittlements/${id}/`,
    method: 'get'
  })
}

/**
 * 创建辐照脆化记录
 * @param {Object} data - 辐照脆化数据
 * @returns {Promise}
 */
export function createEmbrittlement(data) {
  return request({
    url: '/embrittlements/',
    method: 'post',
    data
  })
}

/**
 * 更新辐照脆化记录
 * @param {Number} id - 辐照脆化ID
 * @param {Object} data - 更新的数据
 * @returns {Promise}
 */
export function updateEmbrittlement(id, data) {
  return request({
    url: `/embrittlements/${id}/`,
    method: 'put',
    data
  })
}

/**
 * 删除辐照脆化记录
 * @param {Number} id - 辐照脆化ID
 * @returns {Promise}
 */
export function deleteEmbrittlement(id) {
  return request({
    url: `/embrittlements/${id}/`,
    method: 'delete'
  })
}

/**
 * 批量删除辐照脆化记录
 * @param {Array} ids - 辐照脆化ID数组
 * @returns {Promise}
 */
export function batchDeleteEmbrittlements(ids) {
  return request({
    url: '/embrittlements/batch_delete/',
    method: 'post',
    data: { ids }
  })
}

/**
 * 导出辐照脆化数据
 * @param {Object} data - 导出选项
 * @returns {Promise}
 */
export function exportEmbrittlements(data) {
  return request({
    url: '/embrittlements/export_data/',
    method: 'post',
    data,
    responseType: 'blob'
  })
}

/**
 * 导入辐照脆化数据
 * @param {FormData} formData - 包含文件的FormData
 * @returns {Promise}
 */
export function importEmbrittlements(formData) {
  return request({
    url: '/embrittlements/import_data/',
    method: 'post',
    data: formData,
    headers: {
      'Content-Type': 'multipart/form-data'
    },
    timeout: 60000 // 增加超时时间到60秒，文件上传可能需要更长时间
  })
}

/**
 * 获取材料列表（用于选择材料ID）
 * @returns {Promise}
 */
export function getMaterialList() {
  return request({
    url: '/materials/',
    method: 'get'
  })
}

/**
 * 获取工艺列表（用于选择工艺ID）
 * @returns {Promise}
 */
export function getProcessList() {
  return request({
    url: '/processes/',
    method: 'get'
  })
}

/**
 * 获取辐照条件列表（用于选择辐照ID）
 * @returns {Promise}
 */
export function getIrrConditionList() {
  return request({
    url: '/irrconditions/',
    method: 'get'
  })
}

/**
 * 辐照脆化范围查询
 * @param {Object} data - 查询参数（包含dbtt_min, dbtt_max, dbtt_difference_min, dbtt_difference_max等）
 * @returns {Promise}
 */
export function rangeQueryEmbrittlements(data) {
  return request({
    url: '/embrittlements/range_query/',
    method: 'post',
    data
  })
} 