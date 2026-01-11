import { useState, useEffect, useRef, useCallback } from 'react'

import { useSuggestionContext } from '../contexts/SuggestionContext'

interface UseFeatureSuggestionsReturn {
  suggestions: string[]
  selectedIndices: number[]
  showSuggestions: boolean
  suggestionError: string | null
  handleGetSuggestions: () => Promise<void>
  handleGetMore: () => Promise<void>
  handleAddSelected: (features: string[], onChange: (features: string[]) => void, maxFeatures: number) => void
  handleSkipAll: () => void
  toggleSelection: (index: number) => void
}

export function useFeatureSuggestions(): UseFeatureSuggestionsReturn {
  const { suggestionsEnabled, getSuggestions } = useSuggestionContext()
  const [suggestions, setSuggestions] = useState<string[]>([])
  const [selectedIndices, setSelectedIndices] = useState<number[]>([])
  const [showSuggestions, setShowSuggestions] = useState(false)
  const [suggestionError, setSuggestionError] = useState<string | null>(null)
  const hasFetchedRef = useRef(false), isMountedRef = useRef(true)

  useEffect(() => () => { isMountedRef.current = false }, [])

  const fetchSuggestions = useCallback(async () => {
    setSuggestionError(null)
    try {
      const results = await getSuggestions('features')
      if (isMountedRef.current) {
        setSuggestions(results)
        setSelectedIndices([])
      }
    } catch (err) {
      if (isMountedRef.current) {
        setSuggestionError(err instanceof Error ? err.message : 'Failed to fetch feature suggestions')
        setSuggestions([])
      }
    }
  }, [getSuggestions])

  const handleGetSuggestions = useCallback(async () => {
    setShowSuggestions(true)
    await fetchSuggestions()
  }, [fetchSuggestions])

  const handleGetMore = fetchSuggestions

  useEffect(() => {
    if (suggestionsEnabled && !showSuggestions && !suggestions.length && !hasFetchedRef.current) {
      hasFetchedRef.current = true
      handleGetSuggestions()
    }
  }, [suggestionsEnabled, showSuggestions, suggestions.length, handleGetSuggestions])

  const toggleSelection = useCallback((index: number) => {
    setSelectedIndices((prev) =>
      prev.includes(index) ? prev.filter((i) => i !== index) : [...prev, index]
    )
  }, [])

  const handleSkipAll = useCallback(() => {
    setShowSuggestions(false)
    setSelectedIndices([])
  }, [])

  const handleAddSelected = useCallback((
    features: string[],
    onChange: (features: string[]) => void,
    maxFeatures: number
  ) => {
    onChange([...features.filter((f) => f.trim()), ...selectedIndices.map((i) => suggestions[i])].slice(0, maxFeatures))
    handleSkipAll()
  }, [selectedIndices, suggestions, handleSkipAll])

  return {
    suggestions,
    selectedIndices,
    showSuggestions,
    suggestionError,
    handleGetSuggestions,
    handleGetMore,
    handleAddSelected,
    handleSkipAll,
    toggleSelection,
  }
}
