import { renderHook, act } from '@testing-library/react'
import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest'
import type { Mock } from 'vitest'

import { SuggestionProvider, useSuggestionContext } from '../SuggestionContext'

global.fetch = vi.fn() as Mock

const FIELD_NAME = 'test_field'
const mockResponse = { suggestions: ['Cached'], cost: 0.05 }

describe('SuggestionContext - Caching Behavior', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    const mockFetch = global.fetch as Mock
    mockFetch.mockReset()
  })

  it('should cache suggestions with same context', async () => {
    (global.fetch as Mock).mockResolvedValue({
      ok: true,
      json: async () => mockResponse,
    })

    const { result } = renderHook(() => useSuggestionContext(), {
      wrapper: SuggestionProvider,
    })

    act(() => {
      result.current.setSuggestionsEnabled(true)
      result.current.updateContext('projectName', 'Test')
    })

    await act(async () => {
      await result.current.getSuggestions(FIELD_NAME)
    })

    expect(global.fetch).toHaveBeenCalledTimes(1)

    await act(async () => {
      await result.current.getSuggestions(FIELD_NAME)
    })

    expect(global.fetch).toHaveBeenCalledTimes(1)
  })

  it('should make new request when context changes', async () => {
    (global.fetch as Mock).mockResolvedValue({
      ok: true,
      json: async () => mockResponse,
    })

    const { result } = renderHook(() => useSuggestionContext(), {
      wrapper: SuggestionProvider,
    })

    act(() => {
      result.current.setSuggestionsEnabled(true)
      result.current.updateContext('projectName', 'Test 1')
    })

    await act(async () => {
      await result.current.getSuggestions(FIELD_NAME)
    })

    expect(global.fetch).toHaveBeenCalledTimes(1)

    act(() => {
      result.current.updateContext('projectName', 'Test 2')
    })

    await act(async () => {
      await result.current.getSuggestions(FIELD_NAME)
    })

    expect(global.fetch).toHaveBeenCalledTimes(2)
  })
})

describe('SuggestionContext - Request Payload', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    const mockFetch = global.fetch as Mock
    mockFetch.mockReset()
  })

  it('should send correct request payload', async () => {
    (global.fetch as Mock).mockResolvedValue({
      ok: true,
      json: async () => mockResponse,
    })

    const { result } = renderHook(() => useSuggestionContext(), {
      wrapper: SuggestionProvider,
    })

    act(() => {
      result.current.setSuggestionsEnabled(true)
      result.current.updateContext('projectName', 'My Project')
      result.current.updateContext('platforms', ['web'])
    })

    await act(async () => {
      await result.current.getSuggestions('user_stories', 'current value')
    })

    expect(global.fetch).toHaveBeenCalledWith('/api/suggest', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        field: 'user_stories',
        context: {
          projectName: 'My Project',
          platforms: ['web'],
        },
        current_value: 'current value',
        count: 5,
      }),
    })
  })
})

describe('SuggestionContext - Cache Expiration', () => {
  beforeEach(() => {
    vi.useFakeTimers()
    vi.clearAllMocks()
    const mockFetch = global.fetch as Mock
    mockFetch.mockReset()
  })

  afterEach(() => {
    vi.useRealTimers()
  })

  it('should clean expired cache entries', async () => {
    (global.fetch as Mock).mockResolvedValue({
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

    expect(global.fetch).toHaveBeenCalledTimes(1)

    vi.advanceTimersByTime(6 * 60 * 1000)

    await act(async () => {
      await result.current.getSuggestions(FIELD_NAME)
    })

    expect(global.fetch).toHaveBeenCalledTimes(2)
  })
})
