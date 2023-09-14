<script lang="ts">
	import type { PageData } from './$types'
	import { goto } from '$app/navigation'
	import { Api } from '../../_cli/_api'
	import { onMount } from 'svelte'

	const icons = ['door', 'dragon', 'wizard']

	let metadataModal: HTMLDialogElement
	let contentModal: HTMLDialogElement

	let metadata: string
	let fileName: string
	let fileMime: string
	let fileContent: any | undefined

	function getPassword() {
		if (sessionStorage.password) {
			return sessionStorage.password
		}

		let password: string | null = null
		while (!password) {
			password = prompt('Please insert your password')
		}
		sessionStorage.password = password
		return password
	}

	function getMetadata(_file: { metadata?: string | undefined }) {
		metadata = _file.metadata ?? ''
		metadataModal.showModal()
	}

	async function getFile(_file: { id: string; name: string; mime_type: string }) {
		if (!data.session) {
			return
		}
		const password = getPassword()

		const api = new Api()
		try {
			const file = await api.getFile(_file.id, data.session.username, password)
			fileName = _file.name
			fileMime = _file.mime_type
			fileContent = file
			contentModal.showModal()
		} catch (e) {
			if (e instanceof Error) {
				alert(e.message)
			} else {
				alert('Cannot retrieve file')
			}
		}
	}

	async function shareFile(_file: { id: string }) {
		if (!data.session) {
			return
		}
		const password = getPassword()

		let receiver: string | null = prompt('Who do you want to send this file to?')
		if (!receiver) {
			return
		}

		const api = new Api()
		try {
			await api.shareFile(_file.id, data.session.username, receiver, password)
			alert('File shared successfully')
		} catch (e) {
			if (e instanceof Error) {
				alert(e.message)
			} else {
				alert('Cannot share file')
			}
		}
	}

	async function uploadFile(file: File) {
		if (!data.session) {
			return
		}
		const password = getPassword()

		const api = new Api()
		try {
			const fileData = await api.upload(
				data.session.username,
				//@ts-ignore
				ethereumjs.Buffer.Buffer.from(await file.arrayBuffer()),
				file.name,
				file.type,
				JSON.stringify({
					owner: data.session.username,
					mime_type: file.type
				})
			)
			data.files = await api.getFiles(data.session.username)
			alert('File uploaded successfully')
		} catch (e) {
			if (e instanceof Error) {
				alert(e.message)
			} else {
				alert('Cannot upload file')
			}
		}
	}

	function fileDropped(event: DragEvent) {
		event.preventDefault()
		document.body.style.background = ''

		if (!event.dataTransfer) return

		if (event.dataTransfer.items) {
			// Use DataTransferItemList interface to access the file(s)
			;[...event.dataTransfer.items].forEach((item, i) => {
				// If dropped items aren't files, reject them
				if (item.kind === 'file') {
					const file = item.getAsFile()
					if (!file) return

					uploadFile(file)
				}
			})
		} else {
			// Use DataTransfer interface to access the file(s)
			const file = event.dataTransfer.files[0]
			uploadFile(file)
		}
	}

	export let data: PageData

	if (!data.files) {
		goto('/', {
			invalidateAll: true
		})
	}

	onMount(() => {
		document.body.ondrop = fileDropped
		document.body.ondragover = (event) => {
			event.preventDefault()
		}
		document.body.ondragenter = (event) => {
			document.body.style.background = 'rgb(188 19 24 / .2)'
		}
		document.body.ondragleave = (event) => {
			document.body.style.background = ''
		}
	})
</script>

<div class="absolute inset-0 -z-50 overflow-hidden" aria-hidden="true">
	<svg
		xmlns="http://www.w3.org/2000/svg"
		class="absolute right-0 top-1/2 -z-30 mt-[140px] w-[1140px] -translate-y-1/2 translate-x-[65%]"
		viewBox="0 0 1139.497 1156.258">
		<path
			d="M861.261,311.271S779.156,421.194,744.8,503.292s-105.187,211.842-120.019,229.3-57.669,72.694-167.546,0S414.621,568.922,252.706,462.7-88.46,323.313,48.837,191.586,364.055-1.1,457.235.015s301.742-9.8,365.779,107.531S861.261,311.271,861.261,311.271Z"
			transform="translate(0 682.728) rotate(-52)"
			fill="#df898d" />
	</svg>

	<svg
		xmlns="http://www.w3.org/2000/svg"
		class="absolute right-0 top-1/2 -z-30 mt-[80px] w-[1102px] -translate-y-1/2 translate-x-[66.88%]"
		viewBox="0 0 1101.728 1048.088">
		<path
			d="M861.261,311.271c-11.571,36.271-82.1,109.924-116.462,192.022s-105.187,211.842-120.019,229.3-57.669,72.694-167.546,0S414.621,568.922,252.706,462.7-88.46,323.313,48.837,191.586,364.055-1.1,457.235.015s304.687-5.3,365.779,107.531S872.832,275,861.261,311.271Z"
			transform="translate(801.2 1048.088) rotate(-157)"
			fill="#ecbabc" />
	</svg>

	<img
		src="/dragon.svg"
		class="absolute right-0 top-1/2 -z-30 mt-[40px] -translate-y-1/2 translate-x-[46.38%]"
		alt="" />

	<svg
		xmlns="http://www.w3.org/2000/svg"
		class="absolute right-[5.7%] top-[11.5%] -z-30 w-[55px]"
		viewBox="0 0 55 55">
		<circle cx="27.5" cy="27.5" r="27.5" class="fill-[#FFCEC9]" />
	</svg>

	<svg
		xmlns="http://www.w3.org/2000/svg"
		class="absolute left-[20.26%] top-[95.35%] -z-30 w-[112px]"
		viewBox="0 0 55 55">
		<circle cx="27.5" cy="27.5" r="27.5" class="fill-[#FFCEC9]" />
	</svg>
</div>

<div class="mx-auto w-11/12 max-w-6xl">
	<div class="border-b-pink mt-10 flex justify-between border-b-2 pb-2">
		<div class="font-metshige text-2xl text-[#4A526C]">Your Files</div>
		<div class="flex items-center justify-center gap-4 text-xl">
			<img src="/icons/search-menu.png" alt="" />
			<input type="text" placeholder="Search..." />
		</div>
	</div>

	<div class="my-14 flex min-h-[760px] flex-wrap items-center justify-center gap-8">
		{#each data.files as file, i}
			<div class="border-primary w-64 rounded-3xl border bg-white px-8 py-10">
				<div class="relative">
					<img src="/Scroll {(i % 4) + 1}.png" alt="" class="mx-auto block h-48" />
					<img
						src="/{icons[i % 3]}.png"
						alt=""
						class="w- absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2" />
				</div>
				<div class="mt-4 overflow-hidden text-ellipsis whitespace-nowrap px-1.5 text-xl">
					{file.name}
				</div>
				<div class="-mb-4 mt-5 flex gap-5">
					<button
						on:click={() => {
							getFile(file)
						}}
						class="bg-primary flex h-10 w-10 cursor-pointer items-center justify-center rounded-lg">
						<img src="/icons/read.png" alt="" />
					</button>
					<button
						on:click={() => {
							getMetadata(file)
						}}
						class="bg-primary flex h-10 w-10 cursor-pointer items-center justify-center rounded-lg">
						<img src="/icons/find.png" alt="" />
					</button>
					<button
						on:click={() => {
							shareFile(file)
						}}
						class="bg-primary flex h-10 w-10 cursor-pointer items-center justify-center rounded-lg">
						<img src="/icons/share.png" alt="" />
					</button>
				</div>
			</div>
		{:else}
			You don't have any files
		{/each}
	</div>
</div>

<dialog
	bind:this={metadataModal}
	class="border-primary pointer relative w-11/12 max-w-4xl rounded-2xl border-[3px] bg-white px-12 py-16">
	<button
		on:click={() => {
			metadataModal.close()
		}}
		class="absolute right-5 top-5"><img src="/icons/close.svg" alt="" /></button>

	<div class="grid grid-cols-2 gap-16">
		<div>
			<img src="/castle.svg" alt="" />
		</div>
		<div class="text-xl">
			<div class="font-metshige text-primary mb-4 text-3xl">Info</div>
			<div>
				{metadata}
			</div>
		</div>
	</div>
</dialog>

<dialog
	bind:this={contentModal}
	class="pointer relative aspect-[798/902] w-11/12 max-w-3xl bg-transparent bg-[url(/Scroll.svg)] bg-cover bg-no-repeat px-32">
	<button
		on:click={() => {
			contentModal.close()
		}}
		class="absolute right-[10%] top-[25%]"><img src="/icons/close.svg" alt="" /></button>

	<div class="relative bottom-[23%] top-[30%] h-[41%] text-xl">
		<div class="font-metshige text-primary mb-4 text-center text-3xl">{fileName}</div>
		<div class="relative bottom-0 h-full overflow-y-auto">
			{#if fileContent}
				{#if fileMime === 'text/plain'}
					{fileContent}
				{:else}
					<iframe
						title="Content iframe"
						class="h-full w-full bg-transparent"
						frameborder="0"
						allowtransparency
						src="data:{fileMime};base64,{fileContent.toString('base64')}" />
				{/if}
			{/if}
		</div>
	</div>
</dialog>
