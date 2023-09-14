module.exports = {
	root: true,
	parser: '@typescript-eslint/parser',
	extends: ['eslint:recommended', 'plugin:@typescript-eslint/recommended', 'prettier'],
	plugins: ['@typescript-eslint'],
	overrides: [],
	parserOptions: {
		ecmaVersion: 2020,
		sourceType: 'module'
	},
	env: {
		browser: true,
		es2021: true,
		node: true
	},
	rules: {
		'@typescript-eslint/no-empty-function': 0,
		'@typescript-eslint/no-namespace': [2, { allowDeclarations: true }],
		'@typescript-eslint/no-non-null-assertion': 2,
		'no-prototype-builtins': 0,
		'@typescript-eslint/no-explicit-any': 2,
		'@typescript-eslint/no-unused-vars': [
			1,
			{
				argsIgnorePattern: '^_',
				varsIgnorePattern: '^_',
				caughtErrorsIgnorePattern: '^_'
			}
		]
	}
}
