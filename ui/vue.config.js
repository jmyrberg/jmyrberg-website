const webpack = require('webpack')
// eslint-disable-next-line no-global-assign
require = require('esm')(module)
const { routes } = require('./src/routes')

module.exports = {
  transpileDependencies: [
    'vuetify'
  ],
  css: {
    extract: {
      ignoreOrder: true
    }
  },
  chainWebpack: config => {
    config.plugin('VuetifyLoaderPlugin').tap(args => [{
      progressiveImages: true
    }])
    config.output.globalObject('this')
  },
  configureWebpack: {
    plugins: [
      new webpack.ContextReplacementPlugin(/moment[\\/]locale$/, /^\.\/(en)$/)
    ]
  },
  pluginOptions: {
    webpackBundleAnalyzer: {
      openAnalyzer: false
    },
    compression: {
      modes: [] // Done by GCP
    },
    sitemap: {
      baseURL: 'https://jmyrberg.com',
      defaults: {
        lastmod: '2022-10-12',
        changefreq: 'monthly',
        priority: 0.5
      },
      routes
    }
  },
  parallel: false,
  publicPath: process.env.NODE_ENV === 'production' ? process.env.STATIC_HOST_PREFIX : '/'
}
