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
  context: ProjectContext
  updateContext: (field: string, value: unknown) => void
  suggestionsEnabled: boolean
  setSuggestionsEnabled: (enabled: boolean) => void
  totalCost: number
  addCost: (cost: number) => void
  getSuggestions: (field: string, currentValue?: string) => Promise<string[]>
  isLoading: boolean
}

interface SuggestionCache {
  [key: string]: {
    suggestions: string[]
    timestamp: number
  }
}

interface SuggestionResponse {
  suggestions: string[]
  cost?: number
}

// Constants
const CACHE_TTL_MS = 5 * 60 * 1000
const MAX_CACHE_SIZE = 20

// Create context
const SuggestionContext = createContext<SuggestionContextType | undefined>(undefined)

// Provider component
export function SuggestionProvider({ children }: { children: React.ReactNode }) {
  const [context, setContext] = useState<ProjectContext>({})
  const [suggestionsEnabled, setSuggestionsEnabled] = useState(false)
  const [totalCost, setTotalCost] = useState(0)
  const [isLoading, setIsLoading] = useState(false)
  const [suggestionCache, setSuggestionCache] = useState<SuggestionCache>({})

  const updateContext = useCallback((field: string, value: unknown) => {
    setContext((prev) => ({ ...prev, [field]: value }))
  }, [])

  const addCost = useCallback((cost: number) => {
    setTotalCost((prev) => prev + cost)
  }, [])

  const getSuggestions = useCallback(
    async (field: string, currentValue: string = ''): Promise<string[]> => {
      if (!suggestionsEnabled) {
        return []
      }

      const cacheKey = buildCacheKey(field, context)
      const cached = getCachedSuggestions(suggestionCache, cacheKey)
      if (cached) {
        return cached
      }

      setIsLoading(true)
      try {
        const response = await fetchSuggestionsFromApi(field, context, currentValue)
        updateCacheAndCost(response, cacheKey, addCost, setSuggestionCache)
        return response.suggestions
      } catch (error) {
        console.error('Error fetching suggestions:', error)
        return []
      } finally {
        setIsLoading(false)
      }
    },
    [suggestionsEnabled, context, suggestionCache, addCost]
  )

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
    [context, updateContext, suggestionsEnabled, totalCost, addCost, getSuggestions, isLoading]
  )

  return <SuggestionContext.Provider value={value}>{children}</SuggestionContext.Provider>
}

// Hook to use suggestion context
// eslint-disable-next-line react-refresh/only-export-components
export function useSuggestionContext(): SuggestionContextType {
  const context = useContext(SuggestionContext)
  if (!context) {
    throw new Error('useSuggestionContext must be used within a SuggestionProvider')
  }
  return context
}

// Helper functions (extracted to reduce statement count in getSuggestions)

function buildCacheKey(field: string, ctx: ProjectContext): string {
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
}

function getCachedSuggestions(cache: SuggestionCache, cacheKey: string): string[] | null {
  const cached = cache[cacheKey]
  if (cached && Date.now() - cached.timestamp < CACHE_TTL_MS) {
    return cached.suggestions
  }
  return null
}

async function fetchSuggestionsFromApi(
  field: string,
  context: ProjectContext,
  currentValue: string
): Promise<SuggestionResponse> {
  const response = await fetch('/api/suggest', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ field, context, current_value: currentValue, count: 5 }),
  })

  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to fetch suggestions')
  }

  const data = await response.json()
  return { suggestions: data.suggestions || [], cost: data.cost }
}

function updateCacheAndCost(
  response: SuggestionResponse,
  cacheKey: string,
  addCost: (cost: number) => void,
  setCache: React.Dispatch<React.SetStateAction<SuggestionCache>>
): void {
  if (response.cost) {
    addCost(response.cost)
  }

  setCache((prev) => {
    const updated = {
      ...prev,
      [cacheKey]: { suggestions: response.suggestions, timestamp: Date.now() },
    }
    return cleanAndLimitCache(updated)
  })
}

function cleanAndLimitCache(cache: SuggestionCache): SuggestionCache {
  const now = Date.now()
  const cleaned: SuggestionCache = {}

  Object.entries(cache).forEach(([key, value]) => {
    if (now - value.timestamp < CACHE_TTL_MS) {
      cleaned[key] = value
    }
  })

  if (Object.keys(cleaned).length <= MAX_CACHE_SIZE) {
    return cleaned
  }

  const sorted = Object.entries(cleaned).sort(([, a], [, b]) => b.timestamp - a.timestamp)
  const limited: SuggestionCache = {}
  sorted.slice(0, MAX_CACHE_SIZE).forEach(([key, value]) => {
    limited[key] = value
  })
  return limited
}
