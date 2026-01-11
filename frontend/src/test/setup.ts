import '@testing-library/jest-dom'
import { cleanup } from '@testing-library/react'
import { afterEach, vi } from 'vitest'
import type { Mock } from 'vitest'

// Cleanup after each test
afterEach(() => {
  cleanup()
})

// Mock global fetch if needed
global.fetch = vi.fn() as Mock

// Mock WebSocket
global.WebSocket = vi.fn() as unknown as typeof WebSocket
