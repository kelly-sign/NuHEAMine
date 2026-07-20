import authApi from '@/api/auth';

const state = {
  user: JSON.parse(localStorage.getItem('user')) || null,
  token: localStorage.getItem('access_token') || '',
  refreshToken: localStorage.getItem('refresh_token') || '',
  isAuthenticated: !!localStorage.getItem('access_token')
};

const mutations = {
  SET_USER(state, user) {
    state.user = user;
    localStorage.setItem('user', JSON.stringify(user));
  },
  SET_TOKEN(state, token) {
    state.token = token;
    localStorage.setItem('access_token', token);
  },
  SET_REFRESH_TOKEN(state, refreshToken) {
    state.refreshToken = refreshToken;
    localStorage.setItem('refresh_token', refreshToken);
  },
  SET_AUTH(state, isAuthenticated) {
    state.isAuthenticated = isAuthenticated;
  },
  CLEAR_USER_DATA(state) {
    state.user = null;
    state.token = '';
    state.refreshToken = '';
    state.isAuthenticated = false;
    localStorage.removeItem('user');
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
  }
};

const actions = {
  // 登录
  login({ commit }, { username, password }) {
    return new Promise((resolve, reject) => {
      authApi.login(username, password)
        .then(response => {
          const { user, access, refresh } = response.data;
          commit('SET_USER', user);
          commit('SET_TOKEN', access);
          commit('SET_REFRESH_TOKEN', refresh);
          commit('SET_AUTH', true);
          resolve(response);
        })
        .catch(error => {
          reject(error);
        });
    });
  },

  // 注册
  register({ commit }, { username, password, confirmPassword }) {
    return new Promise((resolve, reject) => {
      authApi.register(username, password, confirmPassword)
        .then(response => {
          const { user, access, refresh } = response.data;
          commit('SET_USER', user);
          commit('SET_TOKEN', access);
          commit('SET_REFRESH_TOKEN', refresh);
          commit('SET_AUTH', true);
          resolve(response);
        })
        .catch(error => {
          reject(error);
        });
    });
  },

  // 获取User信息
  getUserProfile({ commit }) {
    return new Promise((resolve, reject) => {
      authApi.getUserProfile()
        .then(response => {
          const { user } = response.data;
          commit('SET_USER', user);
          resolve(response);
        })
        .catch(error => {
          reject(error);
        });
    });
  },

  // 刷新Token
  refreshToken({ commit, state }) {
    return new Promise((resolve, reject) => {
      // 如果没有刷新令牌，则直接退出登录
      if (!state.refreshToken) {
        commit('CLEAR_USER_DATA');
        reject(new Error('No refresh token available'));
        return;
      }

      authApi.refreshToken(state.refreshToken)
        .then(response => {
          // 检查响应数据
          if (!response || !response.data || !response.data.access) {
            throw new Error('Invalid refresh token response');
          }
          const { access } = response.data;
          commit('SET_TOKEN', access);
          commit('SET_AUTH', true);
          resolve(response);
        })
        .catch(error => {
          console.error('Token refresh failed:');
          commit('CLEAR_USER_DATA');
          reject(error);
        });
    });
  },

  // 退出登录
  logout({ commit }) {
    return new Promise(resolve => {
      authApi.logout();
      commit('CLEAR_USER_DATA');
      resolve();
    });
  }
};

const getters = {
  isAuthenticated: state => state.isAuthenticated,
  currentUser: state => state.user,
  token: state => state.token
};

export default {
  namespaced: true,
  state,
  mutations,
  actions,
  getters
}; 
