import { generateKeyPairSync } from 'crypto'
import jwt from 'jsonwebtoken'

export const TokenType = {
	FILE: 'FILE'
} as const

export type TokenType = (typeof TokenType)[keyof typeof TokenType]

export interface TokenData {
	type: TokenType
}

export class TokenError extends Error {
	constructor(message: string) {
		super(message)
		this.name = 'TokenError'
		Object.setPrototypeOf(this, TokenError.prototype)
	}
}

const __keypair = generateKeyPairSync('rsa', { modulusLength: 4096 })
const JWT_PRIVATE = __keypair.privateKey.export({ type: 'pkcs1', format: 'pem' }).toString()
const JWT_PUBLIC = __keypair.publicKey.export({ type: 'pkcs1', format: 'pem' }).toString()

function createToken(data: object, maxLife: number): string {
	const token = jwt.sign(data, JWT_PRIVATE, {
		algorithm: 'RS256',
		expiresIn: maxLife
	})
	return token
}

function verifyToken<T extends TokenData>(token: string, tokenType: TokenType): T {
	const decoded = jwt.verify(token, JWT_PUBLIC, {
		algorithms: ['RS256']
	}) as T
	if (decoded.type !== tokenType) {
		throw new TokenError('Invalid token: wrong token type')
	}
	return decoded
}

export function createFileToken(userId: string, publicId: string): string {
	return createToken(
		{
			userId,
			publicId,
			type: TokenType.FILE
		},
		60 * 10
	)
}

export interface FileToken extends TokenData {
	userId: string
	publicId: string
}

export function verifyFileToken(token: string): FileToken {
	const obj = verifyToken(token, TokenType.FILE) as FileToken
	if (!obj.userId || !obj.publicId) {
		throw new TokenError('Invalid token: wrong token type')
	}
	return obj
}
