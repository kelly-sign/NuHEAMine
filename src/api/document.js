import request from '@/utils/request'

/**
 * 获取参考文献列表
 * @param {Object} params - 查询参数
 * @returns {Promise}
 */
export function getDocuments(params) {
  return request({
    url: '/documents/',
    method: 'get',
    params: {
      page: params.page || 1,
      page_size: params.page_size || 10,
      doc_name: params.doc_name || '',
      doc_doi: params.doc_doi || ''
    }
  })
}

/**
 * 获取参考文献详情
 * @param {number} id - 文献ID
 * @returns {Promise}
 */
export function getDocumentDetail(id) {
  return request({
    url: `/documents/${id}/`,
    method: 'get'
  })
}

/**
 * 创建参考文献记录
 * @param {Object} data - 参考文献数据
 * @returns {Promise}
 */
export function createDocument(data) {
  // 确保URL格式正确
  const documentData = { ...data };
  if (documentData.doc_url && !documentData.doc_url.startsWith('http://') && !documentData.doc_url.startsWith('https://')) {
    documentData.doc_url = 'https://' + documentData.doc_url;
  }
  
  return request({
    url: '/documents/',
    method: 'post',
    data: documentData
  })
}

/**
 * 更新参考文献记录
 * @param {number} id - 文献ID
 * @param {Object} data - 参考文献数据
 * @returns {Promise}
 */
export function updateDocument(id, data) {
  return request({
    url: `/documents/${id}/`,
    method: 'put',
    data
  })
}

/**
 * 删除参考文献记录
 * @param {number} id - 文献ID
 * @returns {Promise}
 */
export function deleteDocument(id) {
  return request({
    url: `/documents/${id}/`,
    method: 'delete'
  })
}

/**
 * 导入参考文献数据
 * @param {FormData} formData - 包含Excel文件的表单数据
 * @returns {Promise}
 */
export function importDocuments(formData) {
  return request({
    url: '/documents/import_data/',
    method: 'post',
    data: formData,
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

/**
 * 导出参考文献数据
 * @param {Object} data - 导出配置
 * @returns {Promise<Blob>} 返回Blob对象
 */
export function exportDocuments(data) {
  return request({
    url: '/documents/export_data/',
    method: 'post',
    data,
    responseType: 'blob'
  })
} 