import Hapi from '@hapi/hapi'
import { createServer, startServer, stopServer } from './server.js'

let server: Hapi.Server

async function start() {
	try {
		server = await createServer()
		await startServer(server)
	} catch (e) {
		console.error(e)
	}
}
start()

process.on('SIGINT', () => stopServer(server))
process.on('SIGQUIT', () => stopServer(server))
process.on('SIGTERM', () => stopServer(server))
