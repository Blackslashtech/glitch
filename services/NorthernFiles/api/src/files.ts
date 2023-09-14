import Hapi from '@hapi/hapi'
import Boom from '@hapi/boom'
import Joi from 'joi'
import db from './database.js'
import { client } from './auth_api/index.js'
import { sql } from 'kysely'
import { createFileToken, verifyFileToken } from './token-manager.js'
import cron from 'node-cron'
import crypto from 'crypto'

export const filesPlugin: Hapi.Plugin<undefined> = {
	name: 'files',
	dependencies: ['bucket-manager'],
	register(server: Hapi.Server, _options: undefined) {
		server.route([
			{
				method: 'GET',
				path: '/files',
				options: {
					tags: ['api'],
					response: {
						schema: Joi.array().items(
							Joi.object({
								id: Joi.string().uuid().required(),
								name: Joi.string().required(),
								owner: Joi.string().uuid().required(),
								mime_type: Joi.string().required(),
								metadata: Joi.string().optional(),
								key: Joi.string().required()
							})
						)
					}
				},
				handler: async (request: Hapi.Request, h: Hapi.ResponseToolkit) => {
					const { user } = request.auth.credentials
					if (!user) {
						return Boom.unauthorized()
					}

					try {
						const data = await db
							.selectFrom('file_keys')
							.innerJoin('files', 'file_keys.file', 'files.id')
							.select([
								'files.id',
								'files.name',
								'files.owner',
								'files.mime_type',
								'files.metadata',
								'key'
							])
							.where('file_keys.user', '=', user.id)
							.where('uploaded', '=', 1)
							.execute()
						return h.response(
							data.map((el) => ({
								id: el.id,
								name: el.name,
								owner: el.owner,
								mime_type: el.mime_type,
								metadata: el.owner === user.id ? el.metadata?.toString() : undefined,
								key: el.key.toString()
							}))
						)
					} catch (err) {
						return Boom.badImplementation()
					}
				}
			},
			{
				method: 'GET',
				path: '/files/{id}',
				options: {
					tags: ['api'],
					validate: {
						params: Joi.object({
							id: Joi.string().uuid().required()
						})
					},
					response: {
						schema: Joi.object({
							id: Joi.string().uuid().required(),
							name: Joi.string().required(),
							owner: Joi.string().uuid().required(),
							mime_type: Joi.string().required(),
							metadata: Joi.string().optional(),
							key: Joi.string().required()
						})
					}
				},
				handler: async (request: Hapi.Request, h: Hapi.ResponseToolkit) => {
					const { user } = request.auth.credentials
					if (!user) {
						return Boom.unauthorized()
					}
					const id = request.params.id

					try {
						const data = await db
							.selectFrom('file_keys')
							.innerJoin('files', 'file_keys.file', 'files.id')
							.select([
								'files.id',
								'files.name',
								'files.owner',
								'files.mime_type',
								'files.metadata',
								'key'
							])
							.where('file_keys.user', '=', user.id)
							.where('file_keys.file', '=', id)
							.where('uploaded', '=', 1)
							.executeTakeFirst()

						if (!data) {
							return Boom.notFound()
						}

						return h.response({
							id: data.id,
							name: data.name,
							owner: data.owner,
							mime_type: data.mime_type,
							metadata: data.owner === user.id ? data.metadata?.toString() : undefined,
							key: data.key.toString()
						})
					} catch (err) {
						console.error(err)
						return Boom.badImplementation()
					}
				}
			},
			{
				method: 'POST',
				path: '/files',
				options: {
					tags: ['api'],
					validate: {
						payload: Joi.object({
							name: Joi.string().required(),
							mime_type: Joi.string().required(),
							metadata: Joi.string().base64().required(),
							key: Joi.string().required()
						})
					},
					response: {
						schema: Joi.object({
							id: Joi.string().uuid().required(),
							upload_url: Joi.string().uri().required(),
							token: Joi.string().required()
						})
					}
				},
				handler: async (request: Hapi.Request, h: Hapi.ResponseToolkit) => {
					const { user } = request.auth.credentials
					const { name, mime_type, metadata, key } = request.payload as {
						name: string
						mime_type: string
						metadata: string
						key: string
					}
					if (!user) {
						return Boom.unauthorized()
					}

					try {
						const data = await db.transaction().execute(async (trx) => {
							const fileId = crypto.randomUUID()
							await trx
								.insertInto('files')
								.values({
									id: fileId,
									name: name,
									mime_type: mime_type,
									owner: user.id,
									metadata: Buffer.from(metadata, 'base64'),
									uploaded: 0,
									creation_time: new Date()
								})
								.execute()

							const file = await trx
								.selectFrom('files')
								.selectAll()
								.where('id', '=', fileId)
								.executeTakeFirstOrThrow()

							await trx
								.insertInto('file_keys')
								.values({
									file: fileId,
									key: Buffer.from(key),
									user: user.id
								})
								.execute()

							const uploadUrl = await request.server.app.bucketManager.fileUploadUrl(
								user.id,
								fileId,
								request.info.host
							)

							const token = createFileToken(user.id, file.id)

							return {
								id: file.id,
								upload_url: uploadUrl,
								token: token
							}
						})

						return h.response(data)
					} catch {
						return Boom.badImplementation()
					}
				}
			},
			{
				method: 'PUT',
				path: '/files/{id}',
				options: {
					tags: ['api'],
					auth: false,
					validate: {
						params: Joi.object({
							id: Joi.string().uuid().required()
						}),
						payload: Joi.object({
							token: Joi.string().required()
						})
					},
					response: {
						schema: Joi.object({
							details: Joi.string().required()
						})
					}
				},
				handler: async (request: Hapi.Request, h: Hapi.ResponseToolkit) => {
					const id = request.params.id
					const { token } = request.payload as { token: string }

					const { userId, publicId } = verifyFileToken(token)

					if (id !== publicId) {
						return Boom.unauthorized()
					}

					const key = `${userId}/${id}`
					try {
						await request.server.app.bucketManager.checkFile(key)
					} catch {
						return Boom.preconditionFailed()
					}
					try {
						await db
							.updateTable('files')
							.where('id', '=', id)
							.set({
								uploaded: 1
							})
							.execute()

						return h.response({ details: key })
					} catch {
						return Boom.badImplementation()
					}
				}
			},
			{
				method: 'POST',
				path: '/files/{id}/share',
				options: {
					tags: ['api'],
					validate: {
						params: Joi.object({
							id: Joi.string().uuid().required()
						}),
						payload: Joi.object({
							user: Joi.string().required(),
							key: Joi.string().required()
						})
					},
					response: {
						schema: Joi.object({})
					}
				},
				handler: async (request: Hapi.Request, h: Hapi.ResponseToolkit) => {
					const { user } = request.auth.credentials
					const { user: targetUsername, key } = request.payload as { user: string; key: string }
					const id = request.params.id

					if (!user) {
						return Boom.unauthorized()
					}

					const {
						error,
						data: targetUserData,
						response
					} = await client.get('/user/{username}', {
						params: {
							path: {
								username: targetUsername
							}
						}
					})

					if (!response.ok || error || !targetUserData) {
						if (response.status === 404) {
							return Boom.notFound()
						}
						return Boom.badGateway()
					}

					try {
						await db.transaction().execute(async (trx) => {
							// Check file existance and ownership
							const file = await trx
								.selectFrom('files')
								.selectAll()
								.where('owner', '=', user.id)
								.where('id', '=', id)
								.executeTakeFirst()
							if (!file) {
								throw Boom.unauthorized()
							}

							await trx
								.insertInto('file_keys')
								.values({
									file: id,
									key: Buffer.from(key),
									user: targetUserData.id
								})
								.execute()

							const keys = await trx
								.selectFrom('file_keys')
								.select(sql<number>`COUNT(*)`.as('count'))
								.where('user', '=', targetUserData.id)
								.where('file', '=', id)
								.executeTakeFirstOrThrow()

							if (keys.count > 1) {
								throw Boom.conflict()
							}
							if (keys.count !== 1) {
								throw Error('Error in the query')
							}
						})
						return h.response({})
					} catch (e) {
						if (Boom.isBoom(e)) {
							return e
						}
						return Boom.badImplementation()
					}
				}
			}
		])

		cron.schedule('*/5 * * * *', async () => {
			await db
				.deleteFrom('files')
				.where('uploaded', '=', 0)
				.where('creation_time', '<', new Date(Date.now() - 1000 * 15 * 60))
				.execute()
		})
	}
}
