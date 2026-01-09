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
  plugins: ['react-refresh', 'import'],
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

    // Complexity rules - tightened per Issue #78
    // These thresholds enforce maintainable, well-structured code
    complexity: ['error', { max: 15 }], // Cyclomatic complexity (reduced from 20)
    'max-depth': ['error', { max: 4 }], // Nesting depth (unchanged)
    'max-lines': [
      'error',
      { max: 300, skipBlankLines: true, skipComments: true }, // Reduced from 400
    ],
    'max-lines-per-function': [
      'error',
      { max: 150, skipBlankLines: true, skipComments: true }, // Reduced from 320
    ],
    'max-params': ['error', { max: 5 }], // Function parameters (unchanged)
    'max-statements': ['error', { max: 20 }], // Reduced from 25

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
