import { createApp } from 'vue'
import { createPinia } from 'pinia'
// Thêm 2 dòng này
import Toast from 'vue-toastification'
import 'vue-toastification/dist/index.css'

import App from './App.vue'
import router from './router'

const app = createApp(App)

app.use(createPinia())
app.use(router)
// Thêm phần cấu hình toast này
app.use(Toast, {
  position: 'top-right',
  timeout: 3000,
})

app.mount('#app')
