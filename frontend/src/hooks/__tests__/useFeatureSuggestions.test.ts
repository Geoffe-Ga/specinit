import { renderHook, act, waitFor } from '@testing-library/react'
import { describe, it, expect, beforeEach, vi } from 'vitest'

import { useFeatureSuggestions } from '../useFeatureSuggestions'

const mockGetSuggestions = vi.fn()
const mockUseSuggestionContext = vi.fn()

vi.mock('../../contexts/SuggestionContext', () => ({
  useSuggestionContext: () => mockUseSuggestionContext(),
}))

const SUGGESTION_A = 'Suggestion A'
const MOCK_SUGGESTIONS = [SUGGESTION_A, 'Suggestion B', 'Suggestion C']
const FIELD_NAME = 'features'
const FEATURE_A = 'Feature A'

const setupHook = (enabled = false) => {
  mockUseSuggestionContext.mockReturnValue({
    suggestionsEnabled: enabled,
    getSuggestions: mockGetSuggestions,
  })
}

describe('useFeatureSuggestions - Core Behavior', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    setupHook()
  })

  it('should initialize with defaults', () => {
    const { result } = renderHook(() => useFeatureSuggestions())
    expect(result.current.suggestions).toEqual([])
    expect(result.current.selectedIndices).toEqual([])
    expect(result.current.showSuggestions).toBe(false)
    expect(result.current.suggestionError).toBeNull()
  })

  it('should auto-fetch when enabled on mount', async () => {
    mockGetSuggestions.mockResolvedValue(MOCK_SUGGESTIONS)
    setupHook(true)
    const { result } = renderHook(() => useFeatureSuggestions())
    await waitFor(() => {
      expect(result.current.showSuggestions).toBe(true)
      expect(result.current.suggestions).toEqual(MOCK_SUGGESTIONS)
    })
    expect(mockGetSuggestions).toHaveBeenCalledWith(FIELD_NAME)
  })

  it('should not auto-fetch when disabled and only fetch once', async () => {
    renderHook(() => useFeatureSuggestions())
    await new Promise((resolve) => setTimeout(resolve, 100))
    expect(mockGetSuggestions).not.toHaveBeenCalled()

    mockGetSuggestions.mockResolvedValue([FEATURE_A])
    setupHook(true)
    const { rerender } = renderHook(() => useFeatureSuggestions())
    await waitFor(() => expect(mockGetSuggestions).toHaveBeenCalledTimes(1))
    rerender()
    rerender()
    expect(mockGetSuggestions).toHaveBeenCalledTimes(1)
  })
})

describe('useFeatureSuggestions - Error Handling', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    setupHook()
  })

  it('should handle fetch errors and clear on success', async () => {
    mockGetSuggestions.mockRejectedValueOnce(new Error('Network error'))
    const { result } = renderHook(() => useFeatureSuggestions())

    await act(async () => await result.current.handleGetSuggestions())
    expect(result.current.suggestionError).toBe('Network error')
    expect(result.current.suggestions).toEqual([])

    mockGetSuggestions.mockResolvedValueOnce([FEATURE_A])
    await act(async () => await result.current.handleGetMore())
    expect(result.current.suggestionError).toBeNull()
    expect(result.current.suggestions).toEqual([FEATURE_A])
  })

  it('should handle non-Error objects gracefully', async () => {
    mockGetSuggestions.mockRejectedValue('String error')
    const { result } = renderHook(() => useFeatureSuggestions())

    await act(async () => await result.current.handleGetSuggestions())
    expect(result.current.suggestionError).toBe('Failed to fetch feature suggestions')
  })
})

describe('useFeatureSuggestions - Selection Management', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    setupHook()
  })

  it('should toggle selections and clear on skip', () => {
    const { result } = renderHook(() => useFeatureSuggestions())

    act(() => {
      result.current.toggleSelection(0)
      result.current.toggleSelection(2)
    })
    expect(result.current.selectedIndices).toEqual([0, 2])
    act(() => result.current.toggleSelection(0))
    expect(result.current.selectedIndices).toEqual([2])
    act(() => result.current.handleSkipAll())
    expect(result.current.selectedIndices).toEqual([])
    expect(result.current.showSuggestions).toBe(false)
  })
})

describe('useFeatureSuggestions - Feature Merging', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mockGetSuggestions.mockResolvedValue(MOCK_SUGGESTIONS)
    setupHook()
  })

  it('should merge selected suggestions with existing features', async () => {
    const { result } = renderHook(() => useFeatureSuggestions())
    await act(async () => await result.current.handleGetSuggestions())

    act(() => {
      result.current.toggleSelection(0)
      result.current.toggleSelection(2)
    })

    const onChange = vi.fn()
    act(() => result.current.handleAddSelected(['Existing 1', 'Existing 2'], onChange, 10))

    expect(onChange).toHaveBeenCalledWith(['Existing 1', 'Existing 2', SUGGESTION_A, 'Suggestion C'])
    expect(result.current.selectedIndices).toEqual([])
    expect(result.current.showSuggestions).toBe(false)
  })

  it('should filter empty features and respect max limit', async () => {
    const { result } = renderHook(() => useFeatureSuggestions())
    await act(async () => await result.current.handleGetSuggestions())
    act(() => result.current.toggleSelection(0))

    const onChange = vi.fn()
    act(() => result.current.handleAddSelected(['F1', '', '  ', 'F2'], onChange, 10))
    expect(onChange).toHaveBeenCalledWith(['F1', 'F2', SUGGESTION_A])

    act(() => {
      result.current.toggleSelection(0)
      result.current.toggleSelection(1)
      result.current.toggleSelection(2)
    })
    const onChange2 = vi.fn()
    act(() => result.current.handleAddSelected(['Feature 1', 'Feature 2'], onChange2, 3))
    expect(onChange2).toHaveBeenCalledWith(['Feature 1', 'Feature 2', SUGGESTION_A])
  })

  it('should handle empty existing features', async () => {
    const { result } = renderHook(() => useFeatureSuggestions())
    await act(async () => await result.current.handleGetSuggestions())
    act(() => result.current.toggleSelection(1))

    const onChange = vi.fn()
    act(() => result.current.handleAddSelected([], onChange, 10))
    expect(onChange).toHaveBeenCalledWith(['Suggestion B'])
  })
})

describe('useFeatureSuggestions - Fetching & Cleanup', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    setupHook()
  })

  it('should fetch suggestions and reset selection on fetch more', async () => {
    mockGetSuggestions.mockResolvedValueOnce(['Feature A', 'Feature B'])
    const { result } = renderHook(() => useFeatureSuggestions())
    await act(async () => await result.current.handleGetSuggestions())
    expect(result.current.suggestions).toEqual(['Feature A', 'Feature B'])
    expect(result.current.showSuggestions).toBe(true)

    act(() => result.current.toggleSelection(0))
    mockGetSuggestions.mockResolvedValueOnce(['Feature C'])
    await act(async () => await result.current.handleGetMore())
    expect(result.current.suggestions).toEqual(['Feature C'])
    expect(result.current.selectedIndices).toEqual([])
  })

  it('should prevent state updates after unmount', async () => {
    let resolveFetch: (value: string[]) => void
    const fetchPromise = new Promise<string[]>((resolve) => { resolveFetch = resolve })
    mockGetSuggestions.mockReturnValue(fetchPromise)
    const { result, unmount } = renderHook(() => useFeatureSuggestions())
    act(() => { void result.current.handleGetSuggestions() })
    unmount()
    await act(async () => {
      resolveFetch([FEATURE_A])
      await fetchPromise
    })
  })
})
