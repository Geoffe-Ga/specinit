import path from 'path'

import react from '@vitejs/plugin-react'
import { defineConfig } from 'vitest/config'

export default defineConfig({
  plugins: [react()],
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: ['./src/test/setup.ts'],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      exclude: [
        'node_modules/',
        'src/test/',
        '**/*.d.ts',
        '**/*.config.*',
        '**/.eslintrc.cjs',
        '**/mockData',
        'dist/',
        '**/index.ts', // Re-exports only
        'src/main.tsx', // Entry point, not business logic
        'src/App.tsx', // Top-level component, tested via integration
        'src/types.ts', // Type definitions only
        'src/components/GenerationProgress.tsx', // WebSocket integration, E2E tested
        'src/components/GitHubSetup.tsx', // API integration, E2E tested
        'src/components/ProjectForm.tsx', // Form orchestration, E2E tested
        'src/components/FormNavigation.tsx', // Form orchestration, will be tested with E2E
        'src/components/FormProgressIndicator.tsx', // Form orchestration, will be tested with E2E
        'src/components/form-steps/**/*', // Form orchestration components, E2E tested
        'src/components/github/**/*', // GitHub integration components, E2E tested
      ],
      include: [
        'src/contexts/**/*.{ts,tsx}',
        'src/components/**/*.{ts,tsx}',
        'src/utils/**/*.{ts,tsx}',
      ],
      thresholds: {
        lines: 90,
        functions: 90,
        branches: 85,
        statements: 90,
      },
    },
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
})
