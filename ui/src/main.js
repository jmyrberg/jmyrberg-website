import Vue from 'vue'
import App from './App.vue'
import router from './router'
import store from './store'
import vuetify from './plugins/vuetify'
import VueKonva from 'vue-konva'
import axios from 'axios'

const API_URL = process.env.VUE_APP_API_URL
const API_KEY = process.env.VUE_APP_API_KEY

Vue.config.productionTip = false

Vue.use(VueKonva)

export const api = axios.create({
  baseURL: API_URL,
  headers: { common: { 'x-api-key': API_KEY } }
})
Vue.prototype.$api = api
Vue.prototype.$isTouchScreen = function () {
  return ('ontouchstart' in window) || (navigator.MaxTouchPoints > 0) || (navigator.msMaxTouchPoints > 0)
}

new Vue({
  router,
  store,
  vuetify,
  render: h => h(App)
}).$mount('#app')
