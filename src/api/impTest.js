import request from '@/utils/request'

/**
 * 获取冲击测试列表
 * @param {Object} params - 查询参数
 * @returns {Promise}
 */
export function getImpTests(params) {
  return request({
    url: '/imp-tests/',
    method: 'get',
    params
  })
}

/**
 * 获取单个冲击测试
 * @param {Number} id - 冲击测试ID
 * @returns {Promise}
 */
export function getImpTest(id) {
  return request({
    url: `/imp-tests/${id}/`,
    method: 'get'
  })
}

/**
 * 添加冲击测试
 * @param {Object} data - 冲击测试数据
 * @returns {Promise}
 */
export function addImpTest(data) {
  return request({
    url: '/imp-tests/',
    method: 'post',
    data
  })
}

/**
 * 更新冲击测试
 * @param {Number} id - 冲击测试ID
 * @param {Object} data - 更新数据
 * @returns {Promise}
 */
export function updateImpTest(id, data) {
  return request({
    url: `/imp-tests/${id}/`,
    method: 'put',
    data
  })
}

/**
 * 删除冲击测试
 * @param {Number} id - 冲击测试ID
 * @returns {Promise}
 */
export function deleteImpTest(id) {
  return request({
    url: `/imp-tests/${id}/`,
    method: 'delete'
  })
}

/**
 * 导入冲击测试数据
 * @param {FormData} data - 包含文件的表单数据
 * @returns {Promise}
 */
export function importImpTests(data) {
  return request({
    url: '/imp-tests/import_data/',
    method: 'post',
    data,
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

/**
 * 导出冲击测试数据
 * @param {Object} data - 导出参数
 * @returns {Promise}
 */
export function exportImpTests(data) {
  return request({
    url: '/imp-tests/export_data/',
    method: 'post',
    data,
    responseType: 'blob'
  })
} 