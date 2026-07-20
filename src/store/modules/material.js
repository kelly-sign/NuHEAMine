import { 
  getMaterialList, 
  getMaterialDetail,
  createMaterial,
  updateMaterial,
  deleteMaterial,
  importMaterials,
  exportMaterials
} from '@/api/material'

const state = {
  materials: [],
  total: 0,
  currentMaterial: null,
  loading: false
}

const mutations = {
  SET_MATERIALS: (state, { materials, total }) => {
    state.materials = materials
    state.total = total
  },
  SET_CURRENT_MATERIAL: (state, material) => {
    state.currentMaterial = material
  },
  SET_LOADING: (state, loading) => {
    state.loading = loading
  },
  ADD_MATERIAL: (state, material) => {
    state.materials.unshift(material)
    state.total++
  },
  UPDATE_MATERIAL: (state, material) => {
    const index = state.materials.findIndex(item => item.id === material.id)
    if (index !== -1) {
      state.materials.splice(index, 1, material)
    }
  },
  DELETE_MATERIAL: (state, id) => {
    const index = state.materials.findIndex(item => item.id === id)
    if (index !== -1) {
      state.materials.splice(index, 1)
      state.total--
    }
  }
}

const actions = {
  // 获取材料列表
  async getMaterials({ commit }, params) {
    commit('SET_LOADING', true)
    try {
      const { data } = await getMaterialList(params)
      commit('SET_MATERIALS', {
        materials: data.results,
        total: data.count
      })
      return data
    } finally {
      commit('SET_LOADING', false)
    }
  },

  // 获取材料详情
  async getMaterialDetail({ commit }, id) {
    const { data } = await getMaterialDetail(id)
    commit('SET_CURRENT_MATERIAL', data)
    return data
  },

  // 创建材料
  async createMaterial({ commit }, materialData) {
    const { data } = await createMaterial(materialData)
    commit('ADD_MATERIAL', data)
    return data
  },

  // 更新材料
  async updateMaterial({ commit }, { id, data }) {
    const response = await updateMaterial(id, data)
    commit('UPDATE_MATERIAL', response.data)
    return response.data
  },

  // 删除材料
  async deleteMaterial({ commit }, id) {
    await deleteMaterial(id)
    commit('DELETE_MATERIAL', id)
    return true
  },

  // 导入材料数据
  async importMaterials({ dispatch }, file) {
    await importMaterials(file)
    await dispatch('getMaterials')
    return true
  },

  // 导出材料数据
  async exportMaterials(_, params) {
    const response = await exportMaterials(params)
    const url = window.URL.createObjectURL(new Blob([response]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', 'materials.xlsx')
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    return true
  }
}

export default {
  namespaced: true,
  state,
  mutations,
  actions
} 