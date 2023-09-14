import { Api } from '../_cli/_api'
import type { LayoutServerLoad } from './$types'

export const load: LayoutServerLoad = async ({ cookies }) => {
	const api = new Api(
		'http://proxy/',
		async (input: RequestInfo | URL, _init?: RequestInit | undefined) => {
			return await fetch(input, {
				headers: {
					Cookie: `session=${cookies.get('session')}`
				}
			})
		}
	)
	const session = await api.getCurrentUser()
	return {
		session: session,
		files: session ? await api.getFiles(session.username) : []
	}
}
