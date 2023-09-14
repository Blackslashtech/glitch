import Hapi from '@hapi/hapi'
import { Client as MinioClient } from 'minio'

declare global {
	namespace NodeJS {
		interface ProcessEnv {
			BUCKET_NAME: string
			BUCKET_HOST: string
			PUBLIC_HOST: string
			BUCKET_KEY: string
			BUCKET_SECRET: string
		}
	}
}

declare module '@hapi/hapi' {
	interface ServerApplicationState {
		bucketManager: {
			fileUploadUrl: (user: string, mime: string, name: string) => Promise<string>
			checkFile: (name: string) => Promise<void>
		}
	}
}

let minioClient: MinioClient

export const bucketManagerPlugin: Hapi.Plugin<undefined> = {
	name: 'bucket-manager',
	register: async (server: Hapi.Server) => {
		minioClient = new MinioClient({
			endPoint: process.env.BUCKET_HOST ?? 'localhost',
			port: 9000,
			useSSL: false,
			accessKey: process.env.BUCKET_KEY ?? '',
			secretKey: process.env.BUCKET_SECRET ?? ''
		})

		server.app.bucketManager = {
			/**
			 * Presign an upload url a user can use to upload  an image on the bucket
			 * @param user the id of the user requesting the upload, necessary for the final file url
			 * @param id the file name
			 * @param host request.info.host
			 * @returns the presigned url
			 */
			fileUploadUrl: async (user: string, id: string, host: string) => {
				const url = await minioClient.presignedPutObject(
					process.env.BUCKET_NAME,
					`${user}/${id}`,
					5 * 60
				)
				return url.replace(`http://${process.env.BUCKET_HOST}:9000`, `http://${host}`)
			},
			/**
			 * Checks if a file has been uploaded or not
			 * @param id the id of the file (`user_id/file_name`)
			 */
			checkFile: async (id: string) => {
				await minioClient.getObject(process.env.BUCKET_NAME, id)
			}
		}
	}
}
