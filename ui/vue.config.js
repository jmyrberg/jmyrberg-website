module.exports = {
  'transpileDependencies': [
    'vuetify'
  ],
  chainWebpack: config => {
    config.output.globalObject('this')
  },
  publicPath: process.env.NODE_ENV === 'production' ? process.env.STATIC_HOST_PREFIX : '/'
}
