import { defineConfig } from 'vitest/config'
import react from '@vitejs/plugin-react'
import path from 'path'

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
        'src/main.tsx', // Entry point, not business logic
        'src/App.tsx', // Top-level component, tested via integration
        'src/types.ts', // Type definitions only
        'src/components/GenerationProgress.tsx', // WebSocket integration, E2E tested
        'src/components/GitHubSetup.tsx', // API integration, E2E tested
        'src/components/ProjectForm.tsx', // Form orchestration, E2E tested
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
