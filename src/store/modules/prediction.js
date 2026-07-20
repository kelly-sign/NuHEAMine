import {
  getPredictionList,
  getPredictionDetail,
  createPrediction,
  getModelList,
  uploadModel,
  updateModel,
  deleteModel,
  getModelMetrics,
  batchPredict
} from '@/api/prediction'

const state = {
  predictions: [],
  total: 0,
  currentPrediction: null,
  models: [],
  currentModel: null,
  loading: false
}

const mutations = {
  SET_PREDICTIONS: (state, { predictions, total }) => {
    state.predictions = predictions
    state.total = total
  },
  SET_CURRENT_PREDICTION: (state, prediction) => {
    state.currentPrediction = prediction
  },
  SET_MODELS: (state, models) => {
    state.models = models
  },
  SET_CURRENT_MODEL: (state, model) => {
    state.currentModel = model
  },
  SET_LOADING: (state, loading) => {
    state.loading = loading
  },
  ADD_PREDICTION: (state, prediction) => {
    state.predictions.unshift(prediction)
    state.total++
  },
  ADD_MODEL: (state, model) => {
    state.models.unshift(model)
  },
  UPDATE_MODEL: (state, model) => {
    const index = state.models.findIndex(item => item.id === model.id)
    if (index !== -1) {
      state.models.splice(index, 1, model)
    }
  },
  DELETE_MODEL: (state, id) => {
    const index = state.models.findIndex(item => item.id === id)
    if (index !== -1) {
      state.models.splice(index, 1)
    }
  }
}

const actions = {
  // 获取预测记录列表
  async getPredictions({ commit }, params) {
    commit('SET_LOADING', true)
    try {
      const { data } = await getPredictionList(params)
      commit('SET_PREDICTIONS', {
        predictions: data.results,
        total: data.count
      })
      return data
    } finally {
      commit('SET_LOADING', false)
    }
  },

  // 获取预测记录详情
  async getPredictionDetail({ commit }, id) {
    const { data } = await getPredictionDetail(id)
    commit('SET_CURRENT_PREDICTION', data)
    return data
  },

  // 创建预测任务
  async createPrediction({ commit }, predictionData) {
    const { data } = await createPrediction(predictionData)
    commit('ADD_PREDICTION', data)
    return data
  },

  // 获取预测模型列表
  async getModels({ commit }, params) {
    const { data } = await getModelList(params)
    commit('SET_MODELS', data.results)
    return data
  },

  // 上传预测模型
  async uploadModel({ commit }, modelData) {
    const { data } = await uploadModel(modelData)
    commit('ADD_MODEL', data)
    return data
  },

  // 更新预测模型
  async updateModel({ commit }, { id, data }) {
    const response = await updateModel(id, data)
    commit('UPDATE_MODEL', response.data)
    return response.data
  },

  // 删除预测模型
  async deleteModel({ commit }, id) {
    await deleteModel(id)
    commit('DELETE_MODEL', id)
    return true
  },

  // 获取模型评估指标
  async getModelMetrics(_, id) {
    const { data } = await getModelMetrics(id)
    return data
  },

  // 批量预测
  async batchPredict({ dispatch }, data) {
    const response = await batchPredict(data)
    await dispatch('getPredictions')
    return response.data
  }
}

export default {
  namespaced: true,
  state,
  mutations,
  actions
} 