import { createApp } from 'vue'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
import router from './router'
import { createPinia } from 'pinia'
import App from './App.vue'

const app = createApp(App)

// 注册所有图标
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

// 抑制ResizeObserver警告
window.addEventListener('error', (e) => {
  if (e.message.includes('ResizeObserver')) {
    e.preventDefault()
    e.stopPropagation()
    return false
  }
})

// 抑制控制台警告
const originalWarn = console.warn
console.warn = function(...args) {
  if (args[0] && args[0].includes && args[0].includes('ResizeObserver')) {
    return
  }
  originalWarn.apply(console, args)
}

app.use(ElementPlus)
app.use(router)
app.use(createPinia())

app.mount('#app')