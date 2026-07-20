import request from '@/utils/request'

// 获取室温结构性能列表
export function getRoomTempProperties(params) {
  return request({
    url: '/room-temp-properties/',
    method: 'get',
    params: {
      page: params.page || 1,
      page_size: params.page_size || 10,
      material_id: params.material_id || '',
      process_id: params.process_id || '',
      phase_structure: params.phase_structure || '',
      // 添加范围查询参数
      hardness_min: params.hardness_min,
      hardness_max: params.hardness_max,
      yield_strength_c_min: params.yield_strength_c_min,
      yield_strength_c_max: params.yield_strength_c_max,
      yield_strength_t_min: params.yield_strength_t_min,
      yield_strength_t_max: params.yield_strength_t_max,
      ultimate_strength_c_min: params.ultimate_strength_c_min,
      ultimate_strength_c_max: params.ultimate_strength_c_max,
      ultimate_strength_t_min: params.ultimate_strength_t_min,
      ultimate_strength_t_max: params.ultimate_strength_t_max,
      fracture_strain_c_min: params.fracture_strain_c_min,
      fracture_strain_c_max: params.fracture_strain_c_max,
      fracture_strain_t_min: params.fracture_strain_t_min,
      fracture_strain_t_max: params.fracture_strain_t_max
    }
  })
} 