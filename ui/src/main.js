import Vue from 'vue'
import VueRouter from 'vue-router'
import App from './App.vue'
import { routes } from './routes/index.js'
import store from './store'
import axios from 'axios'
import vuetify from './plugins/vuetify'
import VueKonva from 'vue-konva'
import VueApexCharts from 'vue-apexcharts'

const API_URL = process.env.VUE_APP_API_URL
const API_KEY = process.env.VUE_APP_API_KEY

Vue.config.productionTip = false

Vue.use(VueKonva)
Vue.use(VueApexCharts)
Vue.component('ApexChart', VueApexCharts)

Vue.prototype.$isTouchScreen = function () {
  return ('ontouchstart' in window) || (navigator.MaxTouchPoints > 0) || (navigator.msMaxTouchPoints > 0)
}

// API
export const api = axios.create({
  baseURL: API_URL,
  headers: { common: { 'x-api-key': API_KEY } }
})
Vue.prototype.$api = api

// Router
Vue.use(VueRouter)
const router = new VueRouter({
  routes,
  scrollBehavior (to, from, savedPosition) {
    return new Promise((resolve, reject) => {
      setTimeout(() => {
        resolve({ x: 0, y: 0 })
      }, 250)
    })
  }
})

new Vue({
  router,
  store,
  vuetify,
  render: h => h(App)
}).$mount('#app')
