const { defineConfig } = require('@vue/cli-service')

module.exports = defineConfig({
  transpileDependencies: true,
  devServer: {
    port: 8080,
    proxy: {
      '/api': {
        target: process.env.VUE_APP_DEV_PROXY_TARGET || 'http://localhost:8000',
        changeOrigin: true
      }
    }
  }
}) 
