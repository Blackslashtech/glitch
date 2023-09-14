import Hapi from '@hapi/hapi'
import dotenv from 'dotenv'
import { DEFAULT_AUTH, authPlugin } from './auth.js'
import { filesPlugin } from './files.js'
import { bucketManagerPlugin } from './bucket-manager.js'

dotenv.config()

export async function createServer(
	inject?: (server: Hapi.Server) => Promise<void>
): Promise<Hapi.Server> {
	const server: Hapi.Server = Hapi.server({
		port: process.env.PORT || 3000,
		host: process.env.HOST || '0.0.0.0',
		compression: false,
		routes: {
			cors: {
				origin: ['*'],
				headers: ['Content-Type', 'Accept-Language', 'origin', 'accept', 'host', 'date', 'cookie'],
				credentials: true
			}
		}
	})

	await server.register(authPlugin)
	server.auth.strategy(DEFAULT_AUTH, 'auth')
	server.auth.default(DEFAULT_AUTH)

	await server.register([bucketManagerPlugin, filesPlugin])

	if (inject) {
		await inject(server)
	}

	await server.initialize()

	return server
}

export async function startServer(server: Hapi.Server): Promise<Hapi.Server> {
	try {
		await server.start()
		console.log(`Server running on ${server.info.uri}`)
	} catch (e) {
		console.error(e)
	}
	return server
}

export async function stopServer(server: Hapi.Server) {
	await server.stop()
	process.exit(0)
}

process.on('unhandledRejection', (err) => {
	console.log(err)
	process.exit(1)
})
