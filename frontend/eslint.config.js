//  @ts-check

import { tanstackConfig } from '@tanstack/eslint-config'
import prettierConfig from 'eslint-config-prettier'
import prettierPlugin from 'eslint-plugin-prettier'
import pluginQuery from '@tanstack/eslint-plugin-query'

export default [
  {
    ignores: [
      'node_modules/**',
      'dist/**',
      'build/**',
      '*.gen.*',
      'routeTree.gen.ts',
      'vite.config.ts.timestamp-*',
      '*.log',
      '.DS_Store',
      'eslint.config.js',
      'prettier.config.js',
      'vite.config.ts',
    ],
  },
  ...tanstackConfig,
  prettierConfig,
  {
    plugins: {
      prettier: prettierPlugin,
      '@tanstack/query': pluginQuery,
    },
    rules: {
      '@typescript-eslint/no-unnecessary-condition': 'off',
      'prettier/prettier': [
        'error',
        {
          endOfLine: 'auto',
        },
      ],
      // React specific rules
      'react/react-in-jsx-scope': 'off', // Not needed in React 17+
      'react/prop-types': 'off', // Using TypeScript for prop validation
      // TypeScript specific rules
      '@typescript-eslint/no-unused-vars': [
        'error',
        {
          argsIgnorePattern: '^_',
          varsIgnorePattern: '^_',
        },
      ],
      '@typescript-eslint/no-explicit-any': 'warn',
    },
  },
]
