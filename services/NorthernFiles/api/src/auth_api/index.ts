import createClient from 'openapi-fetch'
import { paths } from './schema.d.js'

declare global {
	namespace NodeJS {
		interface ProcessEnv {
			AUTH_HOST: string
		}
	}
}

export const client = createClient<paths>({
	baseUrl: process.env.AUTH_HOST
})
