import Vue from 'vue'
import VueRouter from 'vue-router'

import Home from '../views/Home.vue'
import MaximumFlows from '../views/DemoProjects/MaximumFlows.vue'
import FoodRecommender from '../views/DemoProjects/FoodRecommender.vue'
import DocContextSimilarity from '../views/DemoProjects/DocContextSimilarity.vue'
import Finscraper from '../views/DemoProjects/Finscraper.vue'

Vue.use(VueRouter)

const routes = [
  {
    path: '/',
    alias: '/home',
    name: 'home',
    component: Home
  },
  {
    path: '/demo-projects/maximum-flows',
    name: 'maximum-flows',
    component: MaximumFlows
  },
  {
    path: '/demo-projects/food-recommender/:id?',
    name: 'food-recommender',
    component: FoodRecommender,
    props: true
  },
  {
    path: '/demo-projects/finscraper',
    name: 'finscraper',
    component: Finscraper
  },
  {
    path: '/demo-projects/doc-context-similarity',
    name: 'doc-context-similarity',
    component: DocContextSimilarity
  }
]

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

export default router
