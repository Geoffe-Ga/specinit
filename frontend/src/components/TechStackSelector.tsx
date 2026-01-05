import { useState, useEffect, useRef, useCallback } from 'react'
import { TECH_OPTIONS, type TechStack } from '../types'
import { useSuggestionContext } from '../contexts/SuggestionContext'

interface TechStackSelectorProps {
  value: TechStack
  onChange: (techStack: TechStack) => void
  platforms: string[]
}

// Shared className constants for tech selection buttons
const SELECTED_CLASS = 'bg-blue-600 text-white'
const UNSELECTED_CLASS = 'bg-gray-100 text-gray-700 hover:bg-gray-200'

interface CategorySectionProps {
  title: string
  category: keyof TechStack
  options: string[]
  selectedOptions: string[]
  onToggle: (category: keyof TechStack, option: string) => void
}

function CategorySection({
  title,
  category,
  options,
  selectedOptions,
  onToggle,
}: CategorySectionProps) {
  return (
    <div>
      <h3 className="text-sm font-medium text-gray-700 mb-2">{title}</h3>
      <div className="flex flex-wrap gap-2">
        {options.map((tech) => (
          <button
            key={tech}
            type="button"
            onClick={() => onToggle(category, tech)}
            className={`px-3 py-2 rounded-md text-sm font-medium transition-colors ${
              selectedOptions.includes(tech) ? SELECTED_CLASS : UNSELECTED_CLASS
            }`}
          >
            {tech}
          </button>
        ))}
      </div>
    </div>
  )
}

export function TechStackSelector({ value, onChange, platforms }: TechStackSelectorProps) {
  const { suggestionsEnabled, getSuggestions, isLoading } = useSuggestionContext()
  const [suggestions, setSuggestions] = useState<string[]>([])
  const [showSuggestions, setShowSuggestions] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const hasFetchedRef = useRef(false)
  const isMountedRef = useRef(true)

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      isMountedRef.current = false
    }
  }, [])

  const handleGetSuggestions = useCallback(async () => {
    setShowSuggestions(true)
    setError(null)
    try {
      const results = await getSuggestions('tech_stack')
      if (isMountedRef.current) {
        setSuggestions(results)
      }
    } catch (err) {
      console.error('Failed to get tech stack suggestions:', err)
      if (isMountedRef.current) {
        setError('Failed to load suggestions. Please try again.')
        setSuggestions([])
      }
    }
  }, [getSuggestions])

  // Auto-trigger suggestions when component mounts or when enabled
  useEffect(() => {
    if (suggestionsEnabled && !showSuggestions && suggestions.length === 0 && !hasFetchedRef.current) {
      hasFetchedRef.current = true
      setShowSuggestions(true)
      setError(null)
      getSuggestions('tech_stack')
        .then((results) => {
          if (isMountedRef.current) setSuggestions(results)
        })
        .catch((err) => {
          console.error('Failed to auto-trigger tech stack suggestions:', err)
          if (isMountedRef.current) {
            setError('Failed to load suggestions. Please try again.')
            setSuggestions([])
          }
        })
    }
  }, [suggestionsEnabled, showSuggestions, suggestions.length, getSuggestions])

  const handleAddSuggestion = useCallback((suggestion: string) => {
    // Check if suggestion already exists in any category (prevent cross-category duplicates)
    const alreadyExists = Object.values(value).some((categoryArray) =>
      categoryArray.includes(suggestion)
    )
    if (alreadyExists) return

    // Try to categorize the suggestion based on TECH_OPTIONS
    // Categorization uses substring matching: if suggestion contains a known tech name,
    // it's added to that tech's category (e.g., "React Router" → frontend if "React" is in frontend list)
    let category: keyof TechStack | null = null

    for (const [cat, options] of Object.entries(TECH_OPTIONS)) {
      const match = options.some((opt) => {
        // Escape special regex characters to handle tech names like "Next.js" or "C++"
        const escaped = opt.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
        // Use word boundaries for whole-word matching to avoid false positives
        const regex = new RegExp(`\\b${escaped}\\b`, 'i')
        return regex.test(suggestion)
      })
      if (match) {
        category = cat as keyof TechStack
        break
      }
    }

    // Default to tools if we can't categorize
    if (!category) category = 'tools'

    // Add to appropriate category
    onChange({ ...value, [category]: [...value[category], suggestion] })
  }, [value, onChange])

  const handleSkipAll = () => {
    setShowSuggestions(false)
    setError(null)
  }

  const handleGetMore = useCallback(async () => {
    setError(null)
    try {
      const results = await getSuggestions('tech_stack')
      if (isMountedRef.current) {
        setSuggestions(results)
      }
    } catch (err) {
      console.error('Failed to get more tech stack suggestions:', err)
      if (isMountedRef.current) {
        setError('Failed to load suggestions. Please try again.')
        setSuggestions([])
      }
    }
  }, [getSuggestions])

  const toggleOption = (category: keyof TechStack, option: string) => {
    const current = value[category]
    const updated = current.includes(option)
      ? current.filter((o) => o !== option)
      : [...current, option]
    onChange({ ...value, [category]: updated })
  }

  const showFrontend = platforms.some((p) => ['web', 'ios', 'android', 'desktop'].includes(p))
  const showBackend = !platforms.every((p) => p === 'cli')

  return (
    <div className="space-y-6">
      {/* Loading State */}
      {suggestionsEnabled && showSuggestions && isLoading && suggestions.length === 0 && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div className="flex items-center justify-center gap-2 text-blue-700">
            <span className="animate-spin" aria-hidden="true">🔄</span>
            <span>Generating tech stack recommendations...</span>
          </div>
        </div>
      )}

      {/* Error State */}
      {suggestionsEnabled && showSuggestions && error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <div className="flex items-start gap-2">
            <span className="text-red-600" aria-hidden="true">❌</span>
            <div className="flex-1">
              <p className="text-sm font-medium text-red-800">{error}</p>
              <p className="text-xs text-red-600 mt-1">
                Check your internet connection and API key configuration.
              </p>
            </div>
          </div>
          <div className="flex gap-2 mt-3">
            <button
              type="button"
              onClick={handleGetSuggestions}
              disabled={isLoading}
              className="py-2 px-4 bg-white border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
              aria-label="Retry loading tech stack suggestions"
            >
              {isLoading ? 'Loading...' : 'Try again'}
            </button>
            <button
              type="button"
              onClick={handleSkipAll}
              className="py-2 px-4 bg-white border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50"
              aria-label="Dismiss error and choose manually"
            >
              Dismiss
            </button>
          </div>
        </div>
      )}

      {/* Empty Suggestions State */}
      {suggestionsEnabled && showSuggestions && !error && !isLoading && suggestions.length === 0 && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <p className="text-sm text-yellow-800">
            <span aria-hidden="true">⚠️</span> No suggestions available at this time.
          </p>
          <p className="text-xs text-yellow-600 mt-1">
            Please choose technologies manually below or try again.
          </p>
          <button
            type="button"
            onClick={handleSkipAll}
            className="mt-2 py-2 px-4 bg-white border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50"
            aria-label="Skip suggestions and continue choosing technologies manually"
          >
            Continue manually
          </button>
        </div>
      )}

      {/* Suggestions Display */}
      {suggestionsEnabled && showSuggestions && !error && !isLoading && suggestions.length > 0 && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 space-y-3">
          <p className="text-sm font-medium text-blue-900">
            <span className="sr-only">Recommended technologies for your project</span>
            <span aria-hidden="true">💡</span> Recommended technologies for your project:
          </p>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
            {suggestions.map((suggestion) => {
              const isAdded =
                value.frontend.includes(suggestion) ||
                value.backend.includes(suggestion) ||
                value.database.includes(suggestion) ||
                value.tools.includes(suggestion)

              return (
                <button
                  key={suggestion}
                  type="button"
                  onClick={() => handleAddSuggestion(suggestion)}
                  disabled={isAdded}
                  className={`p-3 text-left text-sm rounded-lg border-2 transition-all ${
                    isAdded
                      ? 'border-green-500 bg-green-50 text-green-900'
                      : 'border-gray-200 bg-white hover:border-blue-300'
                  }`}
                  aria-label={isAdded ? `${suggestion} - already added` : `Add ${suggestion}`}
                >
                  {isAdded ? (
                    <span className="flex items-center gap-2">
                      <span className="text-green-600" aria-hidden="true">✓</span> {suggestion}
                    </span>
                  ) : (
                    suggestion
                  )}
                </button>
              )
            })}
          </div>

          <div className="flex gap-2 pt-2">
            <button
              type="button"
              onClick={handleGetMore}
              disabled={isLoading}
              className="py-2 px-4 bg-white border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
              aria-label="Get more tech stack suggestions"
            >
              {isLoading ? 'Loading...' : 'Get more'}
            </button>
            <button
              type="button"
              onClick={handleSkipAll}
              className="py-2 px-4 bg-white border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50"
              aria-label="Skip suggestions and choose manually"
            >
              Skip all
            </button>
          </div>
        </div>
      )}

      {/* Or choose manually label */}
      {suggestionsEnabled && showSuggestions && suggestions.length > 0 && (
        <div className="text-center">
          <p className="text-sm text-gray-600">Or choose manually:</p>
        </div>
      )}

      {/* Frontend */}
      {showFrontend && (
        <CategorySection
          title="Frontend"
          category="frontend"
          options={TECH_OPTIONS.frontend}
          selectedOptions={value.frontend}
          onToggle={toggleOption}
        />
      )}

      {showBackend && (
        <CategorySection
          title="Backend"
          category="backend"
          options={TECH_OPTIONS.backend}
          selectedOptions={value.backend}
          onToggle={toggleOption}
        />
      )}

      <CategorySection
        title="Database"
        category="database"
        options={TECH_OPTIONS.database}
        selectedOptions={value.database}
        onToggle={toggleOption}
      />

      <CategorySection
        title="Tools"
        category="tools"
        options={TECH_OPTIONS.tools}
        selectedOptions={value.tools}
        onToggle={toggleOption}
      />
    </div>
  )
}
