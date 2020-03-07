import Vue from 'vue'
import Vuex from 'vuex'
import snackbar from './modules/snackbar'

Vue.use(Vuex)

const store = new Vuex.Store({
  modules: {
    snackbar
  }
})

export default store
