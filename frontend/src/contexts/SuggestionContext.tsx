/* eslint-disable react-refresh/only-export-components */
import { createContext, useContext, useState, useCallback, useMemo } from 'react'

// Types
interface ProjectContext {
  projectName?: string
  projectDescription?: string
  platforms?: string[]
  userStory?: {
    role?: string
    action?: string
    outcome?: string
  }
  features?: string[]
  techStack?: {
    frontend?: string[]
    backend?: string[]
    database?: string[]
    tools?: string[]
  }
  aesthetics?: string[]
  additionalContext?: string
}

interface SuggestionContextType {
  // Accumulated form data
  context: ProjectContext
  updateContext: (field: string, value: unknown) => void

  // Suggestion state
  suggestionsEnabled: boolean
  setSuggestionsEnabled: (enabled: boolean) => void

  // Cost tracking
  totalCost: number
  addCost: (cost: number) => void

  // Suggestion fetching
  getSuggestions: (field: string, currentValue?: string) => Promise<string[]>
  isLoading: boolean
}

interface SuggestionCache {
  [key: string]: {
    suggestions: string[]
    timestamp: number
  }
}

// Create context
const SuggestionContext = createContext<SuggestionContextType | undefined>(undefined)

// Cache TTL (5 minutes)
const CACHE_TTL_MS = 5 * 60 * 1000
const MAX_CACHE_SIZE = 20

// Provider component
export function SuggestionProvider({ children }: { children: React.ReactNode }) {
  const [context, setContext] = useState<ProjectContext>({})
  const [suggestionsEnabled, setSuggestionsEnabled] = useState(false)
  const [totalCost, setTotalCost] = useState(0)
  const [isLoading, setIsLoading] = useState(false)
  const [suggestionCache, setSuggestionCache] = useState<SuggestionCache>({})

  // Update context with debouncing handled by the caller
  const updateContext = useCallback((field: string, value: unknown) => {
    setContext((prev) => ({
      ...prev,
      [field]: value,
    }))
  }, [])

  // Add cost to running total
  const addCost = useCallback((cost: number) => {
    setTotalCost((prev) => prev + cost)
  }, [])

  // Generate cache key from field and context
  const getCacheKey = useCallback((field: string, ctx: ProjectContext): string => {
    // Create normalized context (exclude undefined, sort keys)
    const normalized: Record<string, unknown> = {}
    Object.keys(ctx)
      .sort()
      .forEach((key) => {
        const value = ctx[key as keyof ProjectContext]
        if (value !== undefined) {
          normalized[key] = value
        }
      })
    return `${field}:${JSON.stringify(normalized)}`
  }, [])

  // Clean expired cache entries
  const cleanCache = useCallback(() => {
    const now = Date.now()
    setSuggestionCache((prev) => {
      const cleaned: SuggestionCache = {}
      const entries = Object.entries(prev)

      // Keep only non-expired entries
      entries.forEach(([key, value]) => {
        if (now - value.timestamp < CACHE_TTL_MS) {
          cleaned[key] = value
        }
      })

      // If still over max size, keep only most recent
      if (Object.keys(cleaned).length > MAX_CACHE_SIZE) {
        const sorted = Object.entries(cleaned).sort(
          ([, a], [, b]) => b.timestamp - a.timestamp
        )
        const limited: SuggestionCache = {}
        sorted.slice(0, MAX_CACHE_SIZE).forEach(([key, value]) => {
          limited[key] = value
        })
        return limited
      }

      return cleaned
    })
  }, [])

  // Fetch suggestions from API
  const getSuggestions = useCallback(
    async (field: string, currentValue: string = ''): Promise<string[]> => {
      if (!suggestionsEnabled) {
        return []
      }

      // Check cache first
      const cacheKey = getCacheKey(field, context)
      const cached = suggestionCache[cacheKey]
      if (cached && Date.now() - cached.timestamp < CACHE_TTL_MS) {
        return cached.suggestions
      }

      setIsLoading(true)
      try {
        // Call backend API
        const response = await fetch('/api/suggest', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            field,
            context,
            current_value: currentValue,
            count: 5,
          }),
        })

        if (!response.ok) {
          const error = await response.json()
          throw new Error(error.detail || 'Failed to fetch suggestions')
        }

        const data = await response.json()
        const suggestions = data.suggestions || []

        // Update cost
        if (data.cost) {
          addCost(data.cost)
        }

        // Cache the result
        setSuggestionCache((prev) => {
          const newCache = {
            ...prev,
            [cacheKey]: {
              suggestions,
              timestamp: Date.now(),
            },
          }

          // Only clean cache if it's getting full (> 80% of max size)
          const cacheSize = Object.keys(newCache).length
          if (cacheSize > MAX_CACHE_SIZE * 0.8) {
            // Schedule cleanup asynchronously to avoid blocking
            setTimeout(cleanCache, 0)
          }

          return newCache
        })

        return suggestions
      } catch (error) {
        console.error('Error fetching suggestions:', error)
        // Return empty array on error, don't throw
        return []
      } finally {
        setIsLoading(false)
      }
    },
    [suggestionsEnabled, context, suggestionCache, getCacheKey, addCost, cleanCache]
  )

  // Provide context value
  const value = useMemo(
    () => ({
      context,
      updateContext,
      suggestionsEnabled,
      setSuggestionsEnabled,
      totalCost,
      addCost,
      getSuggestions,
      isLoading,
    }),
    [
      context,
      updateContext,
      suggestionsEnabled,
      setSuggestionsEnabled,
      totalCost,
      addCost,
      getSuggestions,
      isLoading,
    ]
  )

  return <SuggestionContext.Provider value={value}>{children}</SuggestionContext.Provider>
}

// Hook to use suggestion context
export function useSuggestionContext() {
  const context = useContext(SuggestionContext)
  if (context === undefined) {
    throw new Error('useSuggestionContext must be used within a SuggestionProvider')
  }
  return context
}
