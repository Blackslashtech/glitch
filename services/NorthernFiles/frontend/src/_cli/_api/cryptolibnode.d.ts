type ClientStep1 = {
	user_id: string
	X_u: string
	alpha: string
}

type ClientStep2 = {
	A_u: string
}

type ServerStep1 = {
	beta: string
	C: string
	X_s: string
}

type ClientStorage = {
	r: string
	user_id: string
	X_u: string
	alpha: string
	x_u: string
}

type Capsule = {
	success: boolean
	user_id: string
	ks: string
	ps: string
	Ps: string
	Pu: string
	C: string
	sk: string
	pk: string
}

export class Module {
	register_user(username: string, password: string): Capsule
	client_step1(username: string, password: string): [ClientStep1, ClientStorage]
	client_step2(ss1: ServerStep1, cs: ClientStorage): ClientStep2
	encrypt_file(raw_file: string, user: Capsule): [string, string]
	retrieve_file(enc_file: string, enc_key: string, user: Capsule, password: string): string
	share_file(
		owner: Capsule,
		receiver: Capsule,
		owner_password: string,
		file_key_owner: string
	): string
	privkey_from_capsule(capsule: Capsule, password: string): string
}

type getter = () => Promise<Module>

export default getter
