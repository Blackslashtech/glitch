import { redirect, type RequestHandler } from '@sveltejs/kit'

export const GET: RequestHandler = async ({ url, cookies }) => {
	const r = url.searchParams.get('url') ?? '/'

	cookies.delete('session', {
		secure: false,
		httpOnly: false
	})

	throw redirect(302, r)
}
