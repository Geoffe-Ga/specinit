import { describe, it, expect, beforeEach, vi } from 'vitest'
import { renderHook, act, waitFor } from '@testing-library/react'
import { SuggestionProvider, useSuggestionContext } from '../SuggestionContext'

// Mock fetch globally
global.fetch = vi.fn()

describe('SuggestionContext', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    // Reset fetch mock
    ;(global.fetch as any).mockReset()
  })

  describe('Context Provider', () => {
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
      // Suppress console.error for this test
      const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {})

      expect(() => {
        renderHook(() => useSuggestionContext())
      }).toThrow('useSuggestionContext must be used within a SuggestionProvider')

      consoleSpy.mockRestore()
    })
  })

  describe('updateContext', () => {
    it('should update context fields', () => {
      const { result } = renderHook(() => useSuggestionContext(), {
        wrapper: SuggestionProvider,
      })

      act(() => {
        result.current.updateContext('projectName', 'Test Project')
      })

      expect(result.current.context.projectName).toBe('Test Project')
    })

    it('should accumulate multiple context updates', () => {
      const { result } = renderHook(() => useSuggestionContext(), {
        wrapper: SuggestionProvider,
      })

      act(() => {
        result.current.updateContext('projectName', 'Test Project')
        result.current.updateContext('platforms', ['web', 'mobile'])
      })

      expect(result.current.context).toEqual({
        projectName: 'Test Project',
        platforms: ['web', 'mobile'],
      })
    })
  })

  describe('setSuggestionsEnabled', () => {
    it('should toggle suggestions enabled state', () => {
      const { result } = renderHook(() => useSuggestionContext(), {
        wrapper: SuggestionProvider,
      })

      expect(result.current.suggestionsEnabled).toBe(false)

      act(() => {
        result.current.setSuggestionsEnabled(true)
      })

      expect(result.current.suggestionsEnabled).toBe(true)
    })
  })

  describe('addCost', () => {
    it('should accumulate cost', () => {
      const { result } = renderHook(() => useSuggestionContext(), {
        wrapper: SuggestionProvider,
      })

      expect(result.current.totalCost).toBe(0)

      act(() => {
        result.current.addCost(0.05)
      })

      expect(result.current.totalCost).toBe(0.05)

      act(() => {
        result.current.addCost(0.10)
      })

      expect(result.current.totalCost).toBeCloseTo(0.15)
    })
  })

  describe('getSuggestions', () => {
    it('should return empty array when suggestions disabled', async () => {
      const { result } = renderHook(() => useSuggestionContext(), {
        wrapper: SuggestionProvider,
      })

      let suggestions: string[] = []
      await act(async () => {
        suggestions = await result.current.getSuggestions('test_field')
      })

      expect(suggestions).toEqual([])
      expect(global.fetch).not.toHaveBeenCalled()
    })

    it('should fetch suggestions when enabled', async () => {
      const mockResponse = {
        suggestions: ['Suggestion 1', 'Suggestion 2', 'Suggestion 3'],
        cost: 0.05,
      }

      ;(global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      })

      const { result } = renderHook(() => useSuggestionContext(), {
        wrapper: SuggestionProvider,
      })

      // Enable suggestions
      act(() => {
        result.current.setSuggestionsEnabled(true)
      })

      let suggestions: string[] = []
      await act(async () => {
        suggestions = await result.current.getSuggestions('test_field')
      })

      expect(suggestions).toEqual(['Suggestion 1', 'Suggestion 2', 'Suggestion 3'])
      expect(result.current.totalCost).toBe(0.05)
    })

    it('should set loading state during fetch', async () => {
      const mockResponse = {
        suggestions: ['Test'],
        cost: 0.01,
      }

      let resolvePromise: (value: any) => void
      const fetchPromise = new Promise((resolve) => {
        resolvePromise = resolve
      })

      ;(global.fetch as any).mockReturnValueOnce(fetchPromise)

      const { result } = renderHook(() => useSuggestionContext(), {
        wrapper: SuggestionProvider,
      })

      act(() => {
        result.current.setSuggestionsEnabled(true)
      })

      // Start fetch (but don't await)
      act(() => {
        result.current.getSuggestions('test_field')
      })

      // Should be loading immediately
      await waitFor(() => {
        expect(result.current.isLoading).toBe(true)
      })

      // Resolve the fetch
      await act(async () => {
        resolvePromise!({ ok: true, json: async () => mockResponse })
        await fetchPromise
      })

      // Should not be loading anymore
      expect(result.current.isLoading).toBe(false)
    })

    it('should handle API errors gracefully', async () => {
      ;(global.fetch as any).mockRejectedValueOnce(new Error('Network error'))

      const { result } = renderHook(() => useSuggestionContext(), {
        wrapper: SuggestionProvider,
      })

      let suggestions: string[] = []

      await act(async () => {
        result.current.setSuggestionsEnabled(true)
        suggestions = await result.current.getSuggestions('test_field')
      })

      // Should return empty array on error
      expect(suggestions).toEqual([])
      expect(result.current.isLoading).toBe(false)
    })

    it('should handle HTTP error responses', async () => {
      ;(global.fetch as any).mockResolvedValueOnce({
        ok: false,
        json: async () => ({ detail: 'Server error' }),
      })

      const { result } = renderHook(() => useSuggestionContext(), {
        wrapper: SuggestionProvider,
      })

      let suggestions: string[] = []

      await act(async () => {
        result.current.setSuggestionsEnabled(true)
        suggestions = await result.current.getSuggestions('test_field')
      })

      expect(suggestions).toEqual([])
    })

    it('should cache suggestions with same context', async () => {
      const mockResponse = {
        suggestions: ['Cached Suggestion'],
        cost: 0.05,
      }

      ;(global.fetch as any).mockResolvedValue({
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

      // First call
      await act(async () => {
        await result.current.getSuggestions('test_field')
      })

      expect(global.fetch).toHaveBeenCalledTimes(1)

      // Second call with same context - should use cache
      await act(async () => {
        await result.current.getSuggestions('test_field')
      })

      // Should still be 1 call (cached)
      expect(global.fetch).toHaveBeenCalledTimes(1)
    })

    it('should make new request when context changes', async () => {
      const mockResponse = {
        suggestions: ['Suggestion'],
        cost: 0.05,
      }

      ;(global.fetch as any).mockResolvedValue({
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

      // First call
      await act(async () => {
        await result.current.getSuggestions('test_field')
      })

      expect(global.fetch).toHaveBeenCalledTimes(1)

      // Change context
      act(() => {
        result.current.updateContext('projectName', 'Test 2')
      })

      // Second call with different context
      await act(async () => {
        await result.current.getSuggestions('test_field')
      })

      // Should make new request (not cached)
      expect(global.fetch).toHaveBeenCalledTimes(2)
    })

    it('should send correct request payload', async () => {
      const mockResponse = {
        suggestions: ['Test'],
        cost: 0.01,
      }

      ;(global.fetch as any).mockResolvedValue({
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

  describe('Cache Management', () => {
    it('should clean expired cache entries', async () => {
      vi.useFakeTimers()

      const mockResponse = {
        suggestions: ['Test'],
        cost: 0.01,
      }

      ;(global.fetch as any).mockResolvedValue({
        ok: true,
        json: async () => mockResponse,
      })

      const { result } = renderHook(() => useSuggestionContext(), {
        wrapper: SuggestionProvider,
      })

      act(() => {
        result.current.setSuggestionsEnabled(true)
      })

      // First call - creates cache entry
      await act(async () => {
        await result.current.getSuggestions('test_field')
      })

      expect(global.fetch).toHaveBeenCalledTimes(1)

      // Fast forward 6 minutes (past 5 min TTL)
      vi.advanceTimersByTime(6 * 60 * 1000)

      // Second call - cache expired, should fetch again
      await act(async () => {
        await result.current.getSuggestions('test_field')
      })

      expect(global.fetch).toHaveBeenCalledTimes(2)

      vi.useRealTimers()
    })
  })
})
