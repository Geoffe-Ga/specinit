import { renderHook, act } from '@testing-library/react'
import { describe, it, expect, beforeEach, vi } from 'vitest'
import type { Mock } from 'vitest'

import { SuggestionProvider, useSuggestionContext } from '../SuggestionContext'

global.fetch = vi.fn() as Mock
const FIELD_NAME = 'test_field'
const mockResponse = { suggestions: ['Test'], cost: 0.01 }

describe('SuggestionContext - Initialization', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    const mockFetch = global.fetch as Mock
    mockFetch.mockReset()
  })

  it('should provide initial context values', () => {
    const { result } = renderHook(() => useSuggestionContext(), {
      wrapper: SuggestionProvider,
    })

    expect(result.current.context).toEqual({})
    expect(result.current.suggestionsEnabled).toBe(false)
    expect(result.current.totalCost).toBe(0)
    expect(result.current.isLoading).toBe(false)
  })

  it('should throw error when used outside provider', () => {
    const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {})
    expect(() => renderHook(() => useSuggestionContext())).toThrow(
      'useSuggestionContext must be used within a SuggestionProvider'
    )
    consoleSpy.mockRestore()
  })
})

describe('SuggestionContext - State Updates', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('should update and accumulate context fields', () => {
    const { result } = renderHook(() => useSuggestionContext(), {
      wrapper: SuggestionProvider,
    })

    act(() => {
      result.current.updateContext('projectName', 'Test Project')
      result.current.updateContext('platforms', ['web'])
    })

    expect(result.current.context).toEqual({
      projectName: 'Test Project',
      platforms: ['web'],
    })
  })

  it('should toggle suggestions and accumulate cost', () => {
    const { result } = renderHook(() => useSuggestionContext(), {
      wrapper: SuggestionProvider,
    })

    act(() => {
      result.current.setSuggestionsEnabled(true)
      result.current.addCost(0.05)
      result.current.addCost(0.1)
    })

    expect(result.current.suggestionsEnabled).toBe(true)
    expect(result.current.totalCost).toBeCloseTo(0.15)
  })
})

describe('SuggestionContext - Fetching', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    const mockFetch = global.fetch as Mock
    mockFetch.mockReset()
  })

  it('should return empty array when disabled', async () => {
    const { result } = renderHook(() => useSuggestionContext(), {
      wrapper: SuggestionProvider,
    })

    let suggestions: string[] = []
    await act(async () => {
      suggestions = await result.current.getSuggestions(FIELD_NAME)
    })

    expect(suggestions).toEqual([])
    expect(global.fetch).not.toHaveBeenCalled()
  })

  it('should fetch suggestions when enabled', async () => {
    (global.fetch as Mock).mockResolvedValueOnce({
      ok: true,
      json: async () => ({ suggestions: ['A', 'B'], cost: 0.05 }),
    })

    const { result } = renderHook(() => useSuggestionContext(), {
      wrapper: SuggestionProvider,
    })

    act(() => {
      result.current.setSuggestionsEnabled(true)
    })

    let suggestions: string[] = []
    await act(async () => {
      suggestions = await result.current.getSuggestions(FIELD_NAME)
    })

    expect(suggestions).toEqual(['A', 'B'])
    expect(result.current.totalCost).toBe(0.05)
  })

  it('should handle errors gracefully', async () => {
    (global.fetch as Mock).mockRejectedValueOnce(new Error('Network error'))

    const { result } = renderHook(() => useSuggestionContext(), {
      wrapper: SuggestionProvider,
    })

    let suggestions: string[] = []
    await act(async () => {
      result.current.setSuggestionsEnabled(true)
      suggestions = await result.current.getSuggestions(FIELD_NAME)
    })

    expect(suggestions).toEqual([])
    expect(result.current.isLoading).toBe(false)
  })

  it('should handle HTTP errors', async () => {
    (global.fetch as Mock).mockResolvedValueOnce({
      ok: false,
      json: async () => ({ detail: 'Server error' }),
    })

    const { result } = renderHook(() => useSuggestionContext(), {
      wrapper: SuggestionProvider,
    })

    let suggestions: string[] = []
    await act(async () => {
      result.current.setSuggestionsEnabled(true)
      suggestions = await result.current.getSuggestions(FIELD_NAME)
    })

    expect(suggestions).toEqual([])
  })
})

describe('SuggestionContext - Loading State', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    const mockFetch = global.fetch as Mock
    mockFetch.mockReset()
  })

  it('should reset loading state after fetch completes', async () => {
    (global.fetch as Mock).mockResolvedValueOnce({
      ok: true,
      json: async () => mockResponse,
    })

    const { result } = renderHook(() => useSuggestionContext(), {
      wrapper: SuggestionProvider,
    })

    act(() => {
      result.current.setSuggestionsEnabled(true)
    })

    await act(async () => {
      await result.current.getSuggestions(FIELD_NAME)
    })

    expect(result.current.isLoading).toBe(false)
  })
})
