import { Api } from './_api'

type Config = {
	server: string
	auth: undefined | string
	username: undefined | string
}

async function cli() {
	const fs = await import('fs')
	const path = await import('path')
	const mime = await import('mime')
	const os = await import('os')
	const yargs = await import('yargs/yargs')
	const hideBin = (await import('yargs/helpers')).hideBin

	function parseConfig(config: string): Config {
		const defaultConfig = {
			server: 'http://localhost/',
			auth: undefined,
			username: undefined
		}
		try {
			const cfg = JSON.parse(fs.readFileSync(config).toString())
			return Object.assign(defaultConfig, cfg)
		} catch (e) {
			return defaultConfig
		}
	}

	function updateConfig(config: string, newData: Partial<Config>) {
		let cfg = {}
		try {
			cfg = JSON.parse(fs.readFileSync(config).toString())
		} catch {
			cfg = {}
		}
		Object.assign(cfg, newData)
		fs.writeFileSync(config, JSON.stringify(cfg))
	}

	yargs(hideBin(process.argv))
		.scriptName('northern-files')
		.usage('$0 <cmd> [args]')
		.command(
			'set-server <host>',
			'Change the remote server to connect to',
			(yargs) => {
				yargs.positional('host', {
					type: 'string'
				})
			},
			function (argv) {
				updateConfig(argv.config as string, {
					server: `http://${argv.host}/`
				})
			}
		)
		.command(
			'register <name> <email> <password>',
			'Create an account',
			(yargs) => {
				yargs
					.positional('name', {
						type: 'string'
					})
					.positional('email', {
						type: 'string'
					})
					.positional('password', {
						type: 'string'
					})
			},
			async function (argv) {
				const cfg = parseConfig(argv.config as string)
				const api = new Api(cfg.server)
				try {
					const data = await api.register(
						argv.name as string,
						argv.email as string,
						argv.password as string
					)
					console.log('Created new user with id', data.id)
				} catch (e) {
					console.error('ERROR:', (e as Error).message)
					process.exit(1)
				}
			}
		)
		.command(
			'login <email> <password>',
			'Login to an existing account',
			(yargs) => {
				yargs
					.positional('email', {
						type: 'string'
					})
					.positional('password', {
						type: 'string'
					})
			},
			async function (argv) {
				const cfg = parseConfig(argv.config as string)
				const api = new Api(cfg.server)
				try {
					const data = await api.login(argv.email as string, argv.password as string)
					updateConfig(
						argv.config as string,
						Object.assign(cfg, { auth: data.token, username: argv.email as string })
					)
					console.log('Logged in successfully')
				} catch (e) {
					console.error('ERROR:', (e as Error).message)
					process.exit(1)
				}
			}
		)
		.command(
			'list-files',
			'Get a list of all your files',
			() => {
				// Do nothing
			},
			async function (argv) {
				const cfg = parseConfig(argv.config as string)
				const api = new Api(cfg.server)
				if (!cfg.username) {
					console.error('ERROR: Unauthenticated')
					process.exit(1)
				}
				try {
					const files = await (async () => {
						if (!cfg.username) {
							console.error('ERROR: Unauthenticated')
							process.exit(1)
						}

						if (!argv.legacy) {
							return await api.getFiles(cfg.username, cfg.auth)
						}

						const readline = (await import('readline')).createInterface({
							input: process.stdin,
							output: process.stdout
						})
						const password = (await new Promise((resolve) => {
							readline.question('Please insert your password: ', (name) => {
								readline.close()
								resolve(name)
							})
						})) as string

						return await api.getFiles(
							cfg.username,
							undefined,
							await api.getPrivateKey(cfg.username, password)
						)
					})()
					if (files.length === 0) {
						console.log("You don't have any file!")
					} else {
						console.log('Here are your files:')
						files.forEach((file) => {
							console.log(`    • ${file.id} (${file.metadata})`)
						})
					}
				} catch (e) {
					console.error('ERROR:', (e as Error).message)
					process.exit(1)
				}
			}
		)
		.command(
			'get-file <file-id> [out-file]',
			'Retrieve a file',
			(yargs) => {
				yargs
					.positional('file-id', {
						type: 'string'
					})
					.positional('out-file', {
						type: 'string'
					})
			},
			async function (argv) {
				const cfg = parseConfig(argv.config as string)
				const api = new Api(cfg.server)
				if (!cfg.username) {
					console.error('ERROR: Unauthenticated')
					process.exit(1)
				}
				const readline = (await import('readline')).createInterface({
					input: process.stdin,
					output: process.stdout
				})
				const password = (await new Promise((resolve) => {
					readline.question('Please insert your password: ', (name) => {
						readline.close()
						resolve(name)
					})
				})) as string
				try {
					const file = await (async () => {
						if (!cfg.username) {
							console.error('ERROR: Unauthenticated')
							process.exit(1)
						}
						if (!argv.legacy) {
							return await api.getFile(argv['file-id'] as string, cfg.username, password, cfg.auth)
						}
						return await api.getFile(
							argv['file-id'] as string,
							cfg.username,
							password,
							undefined,
							await api.getPrivateKey(cfg.username, password)
						)
					})()
					if (argv['out-file']) {
						fs.writeFileSync(argv['out-file'] as string, file)
					} else {
						console.log(file.toString())
					}
				} catch (e) {
					console.error('ERROR:', (e as Error).message)
					process.exit(1)
				}
			}
		)
		.command(
			'upload <file> <metadata>',
			'Upload a new file',
			(yargs) => {
				yargs
					.positional('file', {
						type: 'string'
					})
					.positional('metadata', {
						type: 'string'
					})
			},
			async function (argv) {
				const cfg = parseConfig(argv.config as string)
				const api = new Api(cfg.server)
				if (!cfg.username) {
					console.error('ERROR: Unauthenticated')
					process.exit(1)
				}
				try {
					if (!fs.existsSync(argv.file as string)) {
						throw Error('File is invalid')
					}
					const mime_type = mime.getType(argv.file as string)
					const fileContent = fs.readFileSync(argv.file as string)
					const data = await api.upload(
						cfg.username,
						fileContent,
						path.basename(argv.file as string),
						mime_type ?? 'text/plain',
						argv.metadata as string,
						cfg.auth
					)
					console.log('File successfully uploaded!', `${cfg.server}bucket/${data.details}`)
				} catch (e) {
					console.error('ERROR:', (e as Error).message)
					process.exit(1)
				}
			}
		)
		.command(
			'share <file-id> <user-id>',
			'Share a file with a user',
			(yargs) => {
				yargs
					.positional('file-id', {
						type: 'string'
					})
					.positional('user-id', {
						type: 'string'
					})
			},
			async function (argv) {
				const cfg = parseConfig(argv.config as string)
				const api = new Api(cfg.server)
				if (!cfg.username) {
					console.error('ERROR: Unauthenticated')
					process.exit(1)
				}
				const readline = (await import('readline')).createInterface({
					input: process.stdin,
					output: process.stdout
				})
				const password = (await new Promise((resolve) => {
					readline.question('Please insert your password: ', (name) => {
						readline.close()
						resolve(name)
					})
				})) as string
				try {
					await api.shareFile(
						argv['file-id'] as string,
						cfg.username,
						argv['user-id'] as string,
						password,
						cfg.auth
					)
					console.log('File shared successfully!')
				} catch (e) {
					console.error('ERROR:', (e as Error).message)
					process.exit(1)
				}
			}
		)
		.option('config', {
			alias: 'c',
			type: 'string',
			description: 'Path of config file',
			default: os.homedir() + '/.config/.northern-files'
		})
		.option('legacy', {
			description: 'Use legacy autentication mode'
		})
		.deprecateOption('legacy')
		.demandCommand(1)
		.help()
		.strict()
		.parse()
}

if (typeof window === 'undefined') {
	cli()

	// Weird code to silence the experimental fetch message
	const { emit: originalEmit } = process
	// eslint-disable-next-line @typescript-eslint/ban-ts-comment
	// @ts-ignore
	process.emit = (event, error) =>
		// eslint-disable-next-line @typescript-eslint/ban-ts-comment
		// @ts-ignore
		event === 'warning' && error.name === 'ExperimentalWarning'
			? false
			: // eslint-disable-next-line @typescript-eslint/ban-ts-comment
			  // @ts-ignore
			  originalEmit.apply(process, arguments)
} else {
	throw Error('This file is not supposed to be used here')
}
