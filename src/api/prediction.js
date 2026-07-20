import request from '@/utils/request'

export { predictionEndpoints } from '@/config/predictionEndpoints'

// HV 硬度预测（15 种元素成分）
export function hvPredict(data) {
  return request({
    url: '/predictions/hv/',
    method: 'post',
    timeout: 120000,
    data
  })
}

// 批量 HV 预测（与命令行整表 predict.py 一致，单次子进程）
export function hvPredictBatch(data) {
  return request({
    url: '/predictions/hv/batch/',
    method: 'post',
    timeout: 600000,
    data
  })
}

// 获取预测历史
export function getPredictionHistory(params) {
  return request({
    url: '/predictions/history/',
    method: 'get',
    params
  })
}

// 删除预测记录
export function deletePredictionRecord(id) {
  return request({
    url: `/predictions/history/${id}/`,
    method: 'delete'
  })
}

const toRequestPath = (apiEndpoint) => {
  if (!apiEndpoint || typeof apiEndpoint !== 'string') {
    throw new TypeError('A valid prediction API endpoint is required')
  }

  // request.js already uses a base URL ending in /api. Strip only that public
  // prefix here to avoid generating /api/api/v1/... in production.
  return apiEndpoint.replace(/^\/api(?=\/)/, '')
}

export function submitPrediction(apiEndpoint, data) {
  return request({
    url: toRequestPath(apiEndpoint),
    method: 'post',
    timeout: 120000,
    data
  })
}
