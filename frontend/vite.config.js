import { defineConfig } from 'vite'
import { svelte } from '@sveltejs/vite-plugin-svelte'

// https://vite.dev/config/
export default defineConfig({
  plugins: [svelte()],
  server: {
    // Disable caching for JSON data files during development
    headers: {
      'Cache-Control': 'no-store'
    }
  }
})
