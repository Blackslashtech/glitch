/** @type {import('tailwindcss').Config} */
export default {
	content: ['./src/**/*.{html,js,svelte,ts}'],
	theme: {
		extend: {
			colors: {
				primary: '#BC1318',
				pink: '#ECBABC'
			},
			fontFamily: {
				metshige: 'Metshige',
				playfair: 'Playfair'
			}
		}
	},
	plugins: []
}
