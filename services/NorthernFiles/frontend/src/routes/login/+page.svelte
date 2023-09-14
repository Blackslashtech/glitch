<script lang="ts">
	import { goto } from '$app/navigation'
	import { Api } from '../../_cli/_api'

	let loading = false

	let regData = {
		name: '',
		email: '',
		password: '',
		confirmPassword: ''
	}

	let logData = {
		email: '',
		password: ''
	}

	async function register() {
		if (loading) return
		loading = true

		for (let key in regData) {
			regData[key as keyof typeof regData] = regData[key as keyof typeof regData].trim()
		}

		if (regData.name.length < 5 || regData.email.length < 5 || regData.password.length < 5) {
			loading = false
			return
		}

		if (regData.password !== regData.confirmPassword) {
			alert('Passwords differ')
			loading = false
			return
		}

		const api = new Api()
		try {
			await api.register(regData.name, regData.email, regData.password)
			const auth = await api.login(regData.email, regData.password)
			sessionStorage.password = regData.password
			document.cookie = 'session=' + auth.token + ';max-age=1800'
			goto('/dashboard', {
				invalidateAll: true
			})
		} catch (e) {
			if (e instanceof Error) {
				alert(e.message)
			} else {
				alert('Cannot register user')
			}
		} finally {
			loading = false
		}
	}

	async function login() {
		if (loading) return
		loading = true

		for (let key in logData) {
			logData[key as keyof typeof logData] = logData[key as keyof typeof logData].trim()
		}

		const api = new Api()
		try {
			const auth = await api.login(logData.email, logData.password)
			sessionStorage.password = logData.password
			document.cookie = 'session=' + auth.token + ';max-age=1800'
			goto('/dashboard', {
				invalidateAll: true
			})
		} catch (e) {
			if (e instanceof Error) {
				alert(e.message)
			} else {
				alert('Cannot login')
			}
		} finally {
			loading = false
		}
	}
</script>

<div class="contents" aria-hidden="true">
	<svg
		xmlns="http://www.w3.org/2000/svg"
		class="absolute left-0 top-1/2 -z-30 -mt-[100px] -translate-x-[52%] -translate-y-1/2"
		viewBox="0 0 1163.476 1116.789">
		<path
			d="M898,324.548S812.391,439.16,776.569,524.76,666.9,745.638,651.431,763.841s-60.129,75.794-174.692,0-44.431-170.652-213.253-281.4S-92.233,337.1,50.921,199.759,379.583-1.151,476.738.016,791.351-10.2,858.119,112.133,898,324.548,898,324.548Z"
			transform="translate(1163.477 720.787) rotate(154)"
			class="fill-pink" />
	</svg>

	<svg
		xmlns="http://www.w3.org/2000/svg"
		class="absolute left-0 top-1/2 -z-30 -mt-[100px] -translate-x-[52%] -translate-y-1/2"
		viewBox="0 0 1017.68 933.391">
		<path
			d="M898,324.548S812.391,439.16,776.569,524.76,666.9,745.638,651.431,763.841s-60.129,75.794-174.692,0-44.431-170.652-213.253-281.4S-92.233,337.1,50.921,199.759,379.583-1.151,476.738.016,791.351-10.2,858.119,112.133,898,324.548,898,324.548Z"
			transform="translate(892.228 933.391) rotate(-171)"
			fill="#df898d" />
	</svg>

	<img
		src="/chest.svg"
		class="absolute left-0 top-1/2 -z-30 mt-[40px] -translate-x-[28.57%] -translate-y-1/2"
		alt="" />

	<svg
		xmlns="http://www.w3.org/2000/svg"
		class="absolute left-[16%] top-[20.7%] -z-30 w-[37px]"
		viewBox="0 0 55 55">
		<circle cx="27.5" cy="27.5" r="27.5" class="fill-primary" />
	</svg>

	<svg
		xmlns="http://www.w3.org/2000/svg"
		class="absolute right-[5%] top-[18.5%] -z-30 w-[112px]"
		viewBox="0 0 55 55">
		<circle cx="27.5" cy="27.5" r="27.5" class="fill-pink" />
	</svg>

	<svg
		xmlns="http://www.w3.org/2000/svg"
		class="absolute right-[17.7%] top-[72%] -z-30 w-[55px]"
		viewBox="0 0 55 55">
		<circle cx="27.5" cy="27.5" r="27.5" class="fill-pink" />
	</svg>
</div>

<h1 class="font-metshige mx-auto mt-20 w-[23ch] text-center text-6xl text-[#999999]">
	<span class="text-primary">Easy</span> and <span class="text-primary">secure</span> access to your
	content
</h1>

<h2 class="mt-8 text-center text-2xl text-[#999999]">
	Upload files from your computer, manage them and share them with your friends!
</h2>

<div class="relative">
	<div class="mx-auto mb-52 mt-12 flex max-w-3xl gap-16" class:invisible={loading}>
		<div class="w-full">
			<form
				on:submit|preventDefault={register}
				class="border-primary w-full rounded-2xl border-2 bg-white px-6 py-6">
				<h3 class="font-metshige text-primary mb-6 text-center text-[1.75rem]">Registration</h3>
				<div class="mb-12">
					<input
						type="text"
						class="w-full rounded-2xl border-2 border-[#91919172] bg-white px-9 py-2 text-xl text-[#B8BABA] placeholder:text-[#B8BABA]"
						bind:value={regData.name}
						minlength="5"
						placeholder="Name" />
				</div>
				<div class="mb-12">
					<input
						type="email"
						class="w-full rounded-2xl border-2 border-[#91919172] bg-white px-9 py-2 text-xl text-[#B8BABA] placeholder:text-[#B8BABA]"
						bind:value={regData.email}
						minlength="5"
						placeholder="Email" />
				</div>
				<div class="mb-12">
					<input
						type="password"
						class="w-full rounded-2xl border-2 border-[#91919172] bg-white px-9 py-2 text-xl text-[#B8BABA] placeholder:text-[#B8BABA]"
						bind:value={regData.password}
						minlength="5"
						placeholder="Password" />
				</div>
				<div class="mb-12">
					<input
						type="password"
						class="w-full rounded-2xl border-2 border-[#91919172] bg-white px-9 py-2 text-xl text-[#B8BABA] placeholder:text-[#B8BABA]"
						bind:value={regData.confirmPassword}
						minlength="5"
						placeholder="Confirm password" />
				</div>
				<button
					class="border-primary bg-primary font-metshige hover:text-primary w-full rounded-2xl border-2 py-4 text-xl text-white transition-colors duration-100 hover:bg-white">
					Register Now
				</button>
			</form>
		</div>
		<div class="w-full">
			<form
				on:submit|preventDefault={login}
				class="border-primary w-full rounded-2xl border-2 bg-white px-6 py-6">
				<h3 class="font-metshige text-primary mb-6 text-center text-[1.75rem]">Login</h3>
				<div class="mb-12">
					<input
						type="email"
						class="w-full rounded-2xl border-2 border-[#91919172] bg-white px-9 py-2 text-xl text-[#B8BABA] placeholder:text-[#B8BABA]"
						bind:value={logData.email}
						placeholder="Email" />
				</div>
				<div class="mb-12">
					<input
						type="password"
						class="w-full rounded-2xl border-2 border-[#91919172] bg-white px-9 py-2 text-xl text-[#B8BABA] placeholder:text-[#B8BABA]"
						bind:value={logData.password}
						placeholder="Password" />
				</div>
				<button
					class="border-primary bg-primary font-metshige hover:text-primary w-full rounded-2xl border-2 py-4 text-xl text-white transition-colors duration-100 hover:bg-white">
					Login
				</button>
			</form>
		</div>
	</div>
	<div class="absolute inset-0 flex items-center justify-center" class:hidden={!loading}>
		<svg
			class={`text-primary h-20 w-20 animate-spin`}
			xmlns="http://www.w3.org/2000/svg"
			fill="none"
			viewBox="0 0 24 24">
			<circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
			<path
				class="opacity-75"
				fill="currentColor"
				d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
		</svg>
	</div>
</div>
