import { dirname } from 'node:path'
import { fileURLToPath } from 'node:url'

import { FlatCompat } from '@eslint/eslintrc'
import prettier from 'eslint-config-prettier'

const compat = new FlatCompat({ baseDirectory: dirname(fileURLToPath(import.meta.url)) })

const config = [
  {
    ignores: [
      '.next/**',
      'node_modules/**',
      'coverage/**',
      'playwright-report/**',
      'test-results/**',
      'next-env.d.ts',
      'src/lib/api/schema.d.ts',
    ],
  },
  ...compat.extends('next/core-web-vitals', 'next/typescript', 'plugin:jsx-a11y/recommended'),
  prettier,
  {
    rules: {
      // Design tokens only: no raw hex colours in class names or styles (frontend.md §3).
      'no-restricted-syntax': [
        'error',
        {
          selector: 'Literal[value=/#[0-9a-fA-F]{3,8}\\b/]',
          message: 'Use the CSS variables from globals.css (frontend.md §3), not raw hex colours.',
        },
      ],
      '@typescript-eslint/no-unused-vars': [
        'error',
        { argsIgnorePattern: '^_', varsIgnorePattern: '^_' },
      ],
      '@typescript-eslint/consistent-type-imports': ['error', { prefer: 'type-imports' }],
      'jsx-a11y/anchor-is-valid': 'off',
    },
  },
  {
    files: ['**/*.test.ts', '**/*.test.tsx', 'e2e/**/*.ts', 'vitest.setup.ts'],
    rules: { 'no-restricted-syntax': 'off' },
  },
]

export default config
