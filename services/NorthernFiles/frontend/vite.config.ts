import { sveltekit } from '@sveltejs/kit/vite'
import { defineConfig } from 'vite'

export default defineConfig({
	plugins: [sveltekit()],
	server: {
		proxy: {
			'/api': {
				target: 'http://localhost',
				changeOrigin: true,
				secure: false
			},
			'/bucket': {
				target: 'http://localhost',
				changeOrigin: true,
				secure: false
			}
		}
	}
})
