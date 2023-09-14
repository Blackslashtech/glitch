<script lang="ts">
	import '../app.css'
	import { page } from '$app/stores'
	import type { PageData } from './$types'

	export let data: PageData
</script>

<nav
	class="border-b-primary fixed z-50 flex w-full items-center justify-between border-b-2 bg-white px-24 py-4 font-['Metshige']">
	<div class="flex items-center justify-center gap-16 text-lg">
		<a href="/">
			<div class="border-r-primary flex h-14 items-center justify-center border-r-2 pr-14">
				<img src="/logo.svg" alt="NorthernFiles" />
			</div>
		</a>
		<a href="/" class="pt-2">Home</a>
		<a href="/dashboard" class="pt-2">Dashboard</a>
	</div>
	<div class="flex items-center justify-center gap-9 text-xl">
		{#if !data.session}
			<a href="/login" class="pt-2">Sign In</a>
			<a
				href="/login"
				class="border-primary text-primary hover:bg-primary flex items-center justify-center gap-3 rounded-lg border-2 px-11 transition-colors duration-100 hover:text-white"
				><span
					><svg
						xmlns="http://www.w3.org/2000/svg"
						fill="none"
						viewBox="0 0 24 24"
						stroke-width="1.5"
						stroke="currentColor"
						class="mt-1 h-5 w-5">
						<path stroke-linecap="round" stroke-linejoin="round" d="M12 4.5v15m7.5-7.5h-15" />
					</svg>
				</span><span class="pt-2">Sign Up</span></a>
		{:else}
			<div class="flex items-center justify-center gap-5">
				<img src="/icons/propic.svg" alt="" />
				<div class="flex flex-col justify-center">
					<div class="-mb-1 text-lg">{data.session.name}</div>
					<div class="font-playfair text-sm text-[#919195]">{data.session.username}</div>
				</div>
			</div>
			<a
				href="/logout?url={encodeURIComponent($page.url.pathname)}"
				class="border-primary text-primary hover:bg-primary gap-3 rounded-lg border-2 px-11 pt-2 transition-colors duration-100 hover:text-white"
				>Logout</a>
		{/if}
	</div>
</nav>

<div class="relative mt-24 flex-grow">
	<slot />
</div>

<div class="bg-pink pb-24 pt-9 text-white">
	<div class="mx-auto w-full max-w-7xl">
		<div>
			<img src="/icons/paperplane.svg" alt="newsletter" class="mx-auto block w-12" />
			<div class="mx-auto mt-12 flex max-w-lg">
				<input
					type="text"
					class="w-full rounded-l-2xl border-2 border-white border-r-transparent bg-transparent px-8 py-2 text-xl text-white placeholder:text-white"
					placeholder="Your e-mail..." />
				<button class="font-metshige text-pink -ml-3 rounded-2xl bg-white px-10 pt-1.5 text-xl"
					>Subscribe!</button>
			</div>

			<div class="mt-[69px] flex justify-center gap-28">
				<div class="text-center">
					<div class="font-metshige mb-2 text-xl">About</div>
					<div class="mb-1 font-thin">Carrier</div>
					<div class="mb-1 font-thin">Our Project</div>
				</div>
				<div class="text-center">
					<div class="font-metshige mb-2 text-xl">Contact Us</div>
					<div class="mb-1 font-thin">Email</div>
					<div class="mb-1 font-thin">Support Request</div>
				</div>
			</div>
		</div>

		<footer class="mt-[69px] flex items-center justify-between border-t-2 border-t-white pt-9">
			<div class="font-extralight">All right reserved 2023</div>
			<div class="flex items-center justify-center gap-5">
				<a href="#"><img alt="instagram" src="/icons/instagram.svg" /></a>
				<a href="#"><img alt="facebook" src="/icons/facebook.svg" /></a>
				<a href="#"><img alt="twitter" src="/icons/twitter.svg" /></a>
			</div>
		</footer>
	</div>
</div>
