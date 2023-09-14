import Hapi from '@hapi/hapi'
import HapiSwagger from 'hapi-swagger'
import converter from 'swagger2openapi'
import { createServer, stopServer } from '../src/server.js'

async function start() {
	try {
		const server = await createServer(async (server) => {
			await server.register({
				plugin: HapiSwagger,
				options: {
					swaggerUI: false,
					documentationPage: false,
					info: {
						title: 'API'
					}
				} satisfies HapiSwagger.RegisterOptions
			})

			await server.register({
				name: 'openapi-converter',
				register: async function (server: Hapi.Server) {
					server.route([
						{
							method: 'GET',
							path: '/openapi.json',
							options: {
								auth: false
							},
							handler: async (_request: Hapi.Request, h: Hapi.ResponseToolkit) => {
								const res = await server.inject({
									url: '/swagger.json'
								})
								const data = JSON.parse(res.payload)
								return h.response((await converter.convertObj(data, {})).openapi)
							}
						}
					])
				}
			})
		})
		const data = await server.inject({
			url: '/openapi.json'
		})
		console.log(data.payload)
		await stopServer(server)
	} catch (e) {
		console.error(e)
	}
}
start()
