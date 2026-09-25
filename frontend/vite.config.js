import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  // The project site is published at https://<user>.github.io/AI-BOT/.
  base: '/AI-BOT/',
  plugins: [react()],
  server: { port: 5173 },
})
