import request from '@/utils/request'

export function getHardeningList(params) {
  return request({
    url: '/hardenings/',
    method: 'get',
    params
  })
}

export function getHardeningDetail(id) {
  return request({
    url: `/hardenings/${id}/`,
    method: 'get'
  })
}

export function createHardening(data) {
  return request({
    url: '/hardenings/',
    method: 'post',
    data
  })
}

export function updateHardening(id, data) {
  return request({
    url: `/hardenings/${id}/`,
    method: 'put',
    data
  })
}

export function deleteHardening(id) {
  return request({
    url: `/hardenings/${id}/`,
    method: 'delete'
  })
}

export function batchDeleteHardenings(ids) {
  return request({
    url: '/hardenings/batch_delete/',
    method: 'post',
    data: { ids }
  })
}

export function exportHardenings(data) {
  return request({
    url: '/hardenings/export_data/',
    method: 'post',
    data,
    responseType: 'blob'
  })
}

export function importHardenings(formData) {
  return request({
    url: '/hardenings/import_data/',
    method: 'post',
    data: formData,
    headers: {
      'Content-Type': 'multipart/form-data'
    },
    timeout: 60000
  })
}

export function rangeQueryHardenings(data, params) {
  return request({
    url: '/hardenings/range_query/',
    method: 'post',
    data,
    params
  })
}

export function getHardeningMaterialOptions(params) {
  return request({
    url: '/materials/',
    method: 'get',
    params
  })
}

export function getHardeningProcessOptions(params) {
  return request({
    url: '/processes/',
    method: 'get',
    params
  })
}

export function getHardeningIrradiationOptions(params) {
  return request({
    url: '/irrconditions/',
    method: 'get',
    params
  })
}

export function getHardeningDocumentOptions(params) {
  return request({
    url: '/documents/',
    method: 'get',
    params
  })
}
