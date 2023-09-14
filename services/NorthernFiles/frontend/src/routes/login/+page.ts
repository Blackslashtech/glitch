import { redirect } from '@sveltejs/kit'
import type { PageLoad } from './$types'

export const load: PageLoad = async ({ parent }) => {
	const data = await parent()
	if (data.session) {
		throw redirect(302, '/dashboard')
	}
}
