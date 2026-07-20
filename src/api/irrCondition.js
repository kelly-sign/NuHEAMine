import request from '@/utils/request'

/**
 * 获取辐照条件列表
 * @param {Object} params - 查询参数
 * @returns {Promise}
 */
export function getIrrConditionList(params) {
  return request({
    url: '/irrconditions/',
    method: 'get',
    params
  })
}

/**
 * 获取辐照条件详情
 * @param {Number} id - 辐照ID
 * @returns {Promise}
 */
export function getIrrConditionDetail(id) {
  return request({
    url: `/irrconditions/${id}/`,
    method: 'get'
  })
}

/**
 * 创建辐照条件
 * @param {Object} data - 辐照条件数据
 * @returns {Promise}
 */
export function createIrrCondition(data) {
  return request({
    url: '/irrconditions/',
    method: 'post',
    data
  })
}

/**
 * 更新辐照条件
 * @param {Number} id - 辐照ID
 * @param {Object} data - 更新的数据
 * @returns {Promise}
 */
export function updateIrrCondition(id, data) {
  return request({
    url: `/irrconditions/${id}/`,
    method: 'put',
    data
  })
}

/**
 * 删除辐照条件
 * @param {Number} id - 辐照ID
 * @returns {Promise}
 */
export function deleteIrrCondition(id) {
  return request({
    url: `/irrconditions/${id}/`,
    method: 'delete'
  })
}

/**
 * 批量删除辐照条件
 * @param {Array} ids - 辐照ID数组
 * @returns {Promise}
 */
export function batchDeleteIrrConditions(ids) {
  return request({
    url: '/irrconditions/batch_delete/',
    method: 'post',
    data: { ids }
  })
}

/**
 * 导出辐照条件数据
 * @param {Object} data - 导出选项
 * @returns {Promise}
 */
export function exportIrrConditions(data) {
  return request({
    url: '/irrconditions/export_data/',
    method: 'post',
    data,
    responseType: 'blob'
  })
}

/**
 * 导入辐照条件数据
 * @param {FormData} formData - 包含文件的FormData
 * @returns {Promise}
 */
export function importIrrConditions(formData) {
  return request({
    url: '/irrconditions/import_data/',
    method: 'post',
    data: formData,
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
} 