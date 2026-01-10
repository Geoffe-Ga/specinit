module.exports = {
  root: true,
  env: { browser: true, es2020: true },
  extends: [
    'eslint:recommended',
    'plugin:@typescript-eslint/recommended',
    'plugin:react-hooks/recommended',
    'plugin:import/recommended',
    'plugin:import/typescript',
  ],
  ignorePatterns: ['dist', '.eslintrc.cjs', 'coverage'],
  parser: '@typescript-eslint/parser',
  plugins: ['react-refresh', 'import', 'sonarjs'],
  settings: {
    'import/resolver': {
      typescript: true,
      node: true,
    },
  },
  rules: {
    'react-refresh/only-export-components': [
      'warn',
      { allowConstantExport: true },
    ],
    '@typescript-eslint/no-unused-vars': ['error', { argsIgnorePattern: '^_' }],

    // Complexity rules - World-class standards per Issue #82
    // Tightened from Issue #78 to achieve excellence across all frontend code
    complexity: ['error', { max: 10 }], // Cyclomatic complexity (reduced from 15)
    'max-depth': ['error', { max: 3 }], // Nesting depth (reduced from 4)
    'max-lines': [
      'error',
      { max: 200, skipBlankLines: true, skipComments: true }, // Reduced from 300
    ],
    'max-lines-per-function': [
      'error',
      { max: 75, skipBlankLines: true, skipComments: true }, // Reduced from 150
    ],
    'max-params': ['error', { max: 4 }], // Function parameters (reduced from 5)
    'max-statements': ['error', { max: 15 }], // Reduced from 20

    // SonarJS code quality rules - Issue #82
    'sonarjs/cognitive-complexity': ['error', 10],
    'sonarjs/no-duplicate-string': ['error', { threshold: 3 }],
    'sonarjs/no-identical-functions': 'error',

    // Import organization and boundaries
    'import/no-cycle': 'error', // Circular dependencies
    'import/no-self-import': 'error',
    'import/no-useless-path-segments': 'error',
    'import/default': 'off', // Disable false positives with React/TypeScript
    'import/no-named-as-default-member': 'off', // Disable for React imports
    'import/order': [
      'warn',
      {
        groups: [
          'builtin',
          'external',
          'internal',
          'parent',
          'sibling',
          'index',
        ],
        'newlines-between': 'always',
        alphabetize: { order: 'asc', caseInsensitive: true },
      },
    ],
  },
}
