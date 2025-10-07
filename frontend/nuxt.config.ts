// https://nuxt.com/docs/api/configuration/nuxt-config
import tailwindcss from "@tailwindcss/vite";
export default defineNuxtConfig({
  compatibilityDate: '2025-07-15',
  devtools: { enabled: true },
  modules: ['@nuxt/fonts', '@nuxt/eslint', '@pinia/nuxt'],
  vite: {
    plugins: [tailwindcss()],
  },
  css: ["~/assets/css/main.css"],
  nitro: {
    devProxy: {
      '/api': {
        target: 'http://127.0.0.1:8501',
        changeOrigin: true,
        prependPath: true,
      }
    }
  }
})