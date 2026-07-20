import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import store from './store'
import ElementPlus from 'element-plus'
import en from 'element-plus/es/locale/lang/en'
import 'element-plus/dist/index.css'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'

const app = createApp(App)

// 注册所有图标
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

// 确保按顺序挂载
app.use(store)
app.use(router)
app.use(ElementPlus, { locale: en })

// 等待 router 准备就绪后再挂载
router.isReady().then(() => {
  app.mount('#app')
}) 
