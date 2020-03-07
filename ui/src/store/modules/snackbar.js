const state = {
  message: null,
  color: null,
  snackbar: false
}
const getters = {
  getMessage: (state, getters, rootState) => {
    return state.message
  },
  getSnackbar: (state, getters, rootState) => {
    return state.snackbar
  },
  getSnackbarColor: (state, getters, rootState) => {
    return state.color
  }
}
const actions = {
  showMessage ({ commit, state }, { message, delay, color }) {
    commit('messageOn', { message: message, color: color })
    if (delay > 0) {
      setTimeout(() => { commit('messageOff') }, delay)
    }
  },
  closeMessage ({ commit, state }) {
    commit('messageOff')
  }
}
const mutations = {
  messageOn (state, { message, color }) {
    state.message = message
    state.color = color
    state.snackbar = true
  },
  messageOff (state) {
    state.message = null
    state.color = null
    state.snackbar = false
  }
}
export default {
  namespaced: false,
  state,
  getters,
  actions,
  mutations
}
