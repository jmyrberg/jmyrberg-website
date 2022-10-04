import Vue from 'vue'
import App from './App.vue'
import router from './router'
import store from './store'
import axios from 'axios'
import vuetify from './plugins/vuetify'
import VueKonva from 'vue-konva'

const ENV = process.env.NODE_ENV
const API_URL = process.env.VUE_APP_API_URL
const API_KEY = process.env.VUE_APP_API_KEY

Vue.config.productionTip = false

Vue.use(VueKonva)

export const api = axios.create({
  baseURL: API_URL,
  headers: { common: { 'x-api-key': API_KEY } }
})
api.interceptors.request.use((config) => {
  // Convert /api?param1=bla -> /api/?param1= for Cloud Functions
  if (ENV === 'production' && config.params !== undefined && config.url[config.url.length - 1] !== '/' && config.params.constructor === Object) {
    config.url += '/'
  }
  return config
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
