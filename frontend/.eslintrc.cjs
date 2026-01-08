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

    // Complexity rules - start with lenient baselines, tighten incrementally
    // Current baselines accommodate existing code; see #75 for tightening plan
    complexity: ['error', { max: 20 }], // Cyclomatic complexity (C-rank)
    'max-depth': ['error', { max: 4 }], // Nesting depth
    'max-lines': [
      'error',
      { max: 400, skipBlankLines: true, skipComments: true },
    ],
    'max-lines-per-function': [
      'error',
      { max: 320, skipBlankLines: true, skipComments: true },
    ],
    'max-params': ['error', { max: 5 }], // Function parameters
    'max-statements': ['error', { max: 25 }, { ignoreTopLevelFunctions: false }],

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
