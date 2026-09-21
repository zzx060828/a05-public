import { createApp } from 'vue'
import { createPinia } from 'pinia'

import App from './App.vue'
import router from './router'
import { useUserStore } from './stores/user'

import 'element-plus/dist/index.css'
import ElementPlus from 'element-plus'

import Vant from 'vant'
import 'vant/lib/index.css'


const app = createApp(App)
const pinia = createPinia()

app.use(pinia)
useUserStore(pinia).enableStorageSync()
app.use(router)
app.use(Vant)
app.use(ElementPlus)

app.mount('#app')
