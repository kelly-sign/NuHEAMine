import request from '@/utils/request'

// 获取报告列表
export function getReports(params) {
  return request({
    url: '/reports/',
    method: 'get',
    params
  })
}

// 生成报告
export function generateReport(data) {
  return request({
    url: '/reports/generate/',
    method: 'post',
    data
  })
}

// 获取报告详情
export function getReport(id) {
  return request({
    url: `/reports/${id}/`,
    method: 'get'
  })
}

// 删除报告
export function deleteReport(id) {
  return request({
    url: `/reports/${id}/`,
    method: 'delete'
  })
}

// 下载报告
export function downloadReport(id) {
  return request({
    url: `/reports/${id}/download/`,
    method: 'get',
    responseType: 'blob'
  })
} 