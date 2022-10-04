const webpack = require('webpack')
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
    }
  },
  parallel: false,
  publicPath: process.env.NODE_ENV === 'production' ? process.env.STATIC_HOST_PREFIX : '/'
}
