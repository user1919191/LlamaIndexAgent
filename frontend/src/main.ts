import { createApp } from 'vue'
import { createPinia } from 'pinia'
import './style.css'
import App from './App.vue'
import router from './router'
import { configureHttp } from './api/http'
import { useAuthStore } from './stores/auth'

const app = createApp(App)
const pinia = createPinia()
app.use(pinia).use(router)
configureHttp(() => useAuthStore(pinia), () => router)
app.mount('#app')
