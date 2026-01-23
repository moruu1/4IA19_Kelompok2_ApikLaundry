import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import './assets/main.css'
import './assets/styles/enhancements.css'

console.log('🚀 Starting Laundry App...')

const app = createApp(App)

app.use(createPinia())
app.use(router)

app.mount('#app')

console.log('✅ App mounted successfully!')

// Global error handler
app.config.errorHandler = (err, instance, info) => {
  console.error('Global error:', err, info)
}
