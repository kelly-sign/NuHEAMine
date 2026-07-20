import request from '@/utils/request'

/**
 * 获取微结构演化列表
 * @param {Object} params - 查询参数
 * @returns {Promise}
 */
export function getMicrostructureList(params) {
  return request({
    url: '/microstructures/',
    method: 'get',
    params
  })
}

/**
 * 获取微结构演化详情
 * @param {Number} id - 微结构ID
 * @returns {Promise}
 */
export function getMicrostructureDetail(id) {
  return request({
    url: `/microstructures/${id}/`,
    method: 'get'
  })
}

/**
 * 创建微结构演化记录
 * @param {Object} data - 微结构演化数据
 * @returns {Promise}
 */
export function createMicrostructure(data) {
  return request({
    url: '/microstructures/',
    method: 'post',
    data
  })
}

/**
 * 更新微结构演化记录
 * @param {Number} id - 微结构ID
 * @param {Object} data - 更新的数据
 * @returns {Promise}
 */
export function updateMicrostructure(id, data) {
  return request({
    url: `/microstructures/${id}/`,
    method: 'put',
    data
  })
}

/**
 * 删除微结构演化记录
 * @param {Number} id - 微结构ID
 * @returns {Promise}
 */
export function deleteMicrostructure(id) {
  return request({
    url: `/microstructures/${id}/`,
    method: 'delete'
  })
}

/**
 * 批量删除微结构演化记录
 * @param {Array} ids - 微结构ID数组
 * @returns {Promise}
 */
export function batchDeleteMicrostructures(ids) {
  return request({
    url: '/microstructures/batch_delete/',
    method: 'post',
    data: { ids }
  })
}

/**
 * 导出微结构演化数据
 * @param {Object} data - 导出选项
 * @returns {Promise}
 */
export function exportMicrostructures(data) {
  return request({
    url: '/microstructures/export_data/',
    method: 'post',
    data,
    responseType: 'blob'
  })
}

/**
 * 导入微结构演化数据
 * @param {FormData} formData - 包含文件的FormData
 * @returns {Promise}
 */
export function importMicrostructures(formData) {
  return request({
    url: '/microstructures/import/',
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