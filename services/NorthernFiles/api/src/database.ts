import { Kysely, MysqlDialect } from 'kysely'
import { DB } from './db.d.js'
import { createPool } from 'mysql2'

declare global {
	namespace NodeJS {
		interface ProcessEnv {
			DATABASE_USER: string
			DATABASE_PASSWORD: string
			DATABASE_HOST: string
			DATABASE_DB: string
		}
	}
}

const db = new Kysely<DB>({
	dialect: new MysqlDialect({
		pool: createPool({
			user: process.env.DATABASE_USER,
			password: process.env.DATABASE_PASSWORD,
			host: process.env.DATABASE_HOST,
			database: process.env.DATABASE_DB
		})
	})
})

export default db
