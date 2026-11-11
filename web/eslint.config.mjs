import nextCoreWebVitals from 'eslint-config-next/core-web-vitals'
import nextTypescript from 'eslint-config-next/typescript'
import prettier from 'eslint-config-prettier'
import jsxA11y from 'eslint-plugin-jsx-a11y'

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
  // eslint-config-next ships native flat configs from v16; they must not be
  // wrapped in FlatCompat, which cannot serialize them.
  ...nextCoreWebVitals,
  ...nextTypescript,
  prettier,
  {
    rules: {
      // eslint-config-next already registers the jsx-a11y plugin, so take its
      // recommended rules rather than the config (which would redefine it).
      ...jsxA11y.flatConfigs.recommended.rules,
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
