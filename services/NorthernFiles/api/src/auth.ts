import Hapi from '@hapi/hapi'
import Boom from '@hapi/boom'
import jwksClient from 'jwks-rsa'
import jwt from 'jsonwebtoken'
import Joi from 'joi'

export const DEFAULT_AUTH = 'DEFAULT_AUTH'

declare module '@hapi/hapi' {
	interface AuthCredentials {
		sessionToken: string
	}

	interface UserCredentials {
		id: string
		username: string
		publicKey: string
	}
}

declare global {
	namespace NodeJS {
		interface ProcessEnv {
			AUTH_HOST: string
		}
	}
}

const JWT_PAYLOAD_SCHEMA: Joi.Schema<Hapi.UserCredentials> = Joi.object({
	id: Joi.string().uuid().required(),
	username: Joi.string().required(),
	name: Joi.string().required()
})

export const authPlugin: Hapi.Plugin<undefined> = {
	name: 'auth',
	dependencies: [],
	register(server: Hapi.Server, _options: undefined) {
		server.state('session', {
			ttl: null,
			isSecure: false,
			isHttpOnly: true,
			encoding: 'none',
			path: '/'
		})

		server.auth.scheme('auth', authScheme)

		server.route({
			method: 'GET',
			path: '/user',
			options: {
				tags: ['api'],
				response: {
					schema: JWT_PAYLOAD_SCHEMA
				}
			},
			handler: async (request: Hapi.Request, h: Hapi.ResponseToolkit) => {
				return h.response(request.auth.credentials.user)
			}
		})
	}
}

const decodeJWT = (token: string) => {
	return new Promise((resolve, reject) => {
		const client = jwksClient({
			jwksUri: `${process.env.AUTH_HOST}/jwks`
		})

		jwt.verify(
			token,
			(header: jwt.JwtHeader, callback: jwt.SigningKeyCallback) => {
				client.getSigningKey(header.kid, function (err, key) {
					if (err) {
						callback(err, undefined)
					}

					const signingKey = key?.getPublicKey()
					callback(err, signingKey)
				})
			},
			{},
			(err: jwt.VerifyErrors | null, decoded: string | jwt.Jwt | jwt.JwtPayload | undefined) => {
				if (decoded && !err) {
					resolve(decoded)
				} else {
					reject(err)
				}
			}
		)
	}) satisfies Promise<string | jwt.Jwt | jwt.JwtPayload>
}

const authScheme: Hapi.ServerAuthScheme = (_server: Hapi.Server, _options: object | undefined) => {
	const schemeObject: Hapi.ServerAuthSchemeObject = {
		authenticate: async (request: Hapi.Request, h: Hapi.ResponseToolkit) => {
			const { session: sessionToken } = request.state

			if (!sessionToken) {
				throw Boom.unauthorized()
			}

			try {
				const body = await decodeJWT(sessionToken)
				const { error, value: payload } = JWT_PAYLOAD_SCHEMA.validate(body)
				if (error) {
					h.unstate('session')
					throw Boom.unauthorized()
				}

				return h.authenticated({
					credentials: {
						sessionToken: sessionToken,
						user: payload
					}
				})
			} catch {
				h.unstate('session')
				throw Boom.unauthorized()
			}
		}
	}

	return schemeObject
}
