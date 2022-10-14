const Home = () => import(/* webpackChunkName: "home" */ '../views/Home.vue')
const Forecaster = () => import(/* webpackChunkName: "forecaster" */ '../views/DemoProjects/Forecaster.vue')
const MaximumFlows = () => import(/* webpackChunkName: "maximum-flows" */ '../views/DemoProjects/MaximumFlows.vue')
const FoodRecommender = () => import(/* webpackChunkName: "food-recommender" */ '../views/DemoProjects/FoodRecommender.vue')
const DocContextSimilarity = () => import(/* webpackChunkName: "doc-context-similarity" */ '../views/DemoProjects/DocContextSimilarity.vue')
const Finscraper = () => import(/* webpackChunkName: "finscraper" */ '../views/DemoProjects/Finscraper.vue')

export const routes = [
  {
    path: '/',
    alias: '/home',
    name: 'home',
    component: Home,
    meta: {
      sitemap: {
        lastmod: '2022-10-12',
        priority: 0.8,
        changefreq: 'monthly'
      }
    }
  },
  {
    path: '/demo-projects/forecaster',
    name: 'forecaster',
    component: Forecaster,
    meta: {
      sitemap: {
        lastmod: '2022-10-12',
        priority: 0.5,
        changefreq: 'monthly'
      }
    }
  },
  {
    path: '/demo-projects/maximum-flows',
    name: 'maximum-flows',
    component: MaximumFlows,
    meta: {
      sitemap: {
        lastmod: '2022-10-12',
        priority: 0.5,
        changefreq: 'monthly'
      }
    }
  },
  {
    path: '/demo-projects/food-recommender/:id?',
    name: 'food-recommender',
    component: FoodRecommender,
    props: true,
    meta: {
      sitemap: {
        slugs: [
          {
            id: '',
            lastmod: '2022-10-12',
            priority: 0.5,
            changefreq: 'monthly'
          }
        ]
      }
    }
  },
  {
    path: '/demo-projects/finscraper',
    name: 'finscraper',
    component: Finscraper,
    meta: {
      sitemap: {
        lastmod: '2022-10-12',
        priority: 0.5,
        changefreq: 'monthly'
      }
    }
  },
  {
    path: '/demo-projects/doc-context-similarity',
    name: 'doc-context-similarity',
    component: DocContextSimilarity,
    meta: {
      sitemap: {
        lastmod: '2022-10-12',
        priority: 0.5,
        changefreq: 'monthly'
      }
    }
  }
]
