// src/main.ts
import { createApp } from 'vue'
import App from './App.vue'

// Vuetify
import 'vuetify/styles'
import { createVuetify } from 'vuetify'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'
import '@mdi/font/css/materialdesignicons.css' // ← required for v-icon

const vuetify = createVuetify({
  theme: {
    defaultTheme: 'dark',
  },
  components,
  directives,
})

createApp(App).use(vuetify).mount('#app')
