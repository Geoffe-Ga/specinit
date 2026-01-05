import { useState, useEffect } from 'react'
import type { UserStory } from '../types'
import type { FieldErrors } from 'react-hook-form'
import { useSuggestionContext } from '../contexts/SuggestionContext'

interface UserStoryInputProps {
  value: UserStory
  onChange: (userStory: UserStory) => void
  errors?: FieldErrors<UserStory>
}

interface ParsedUserStory {
  role: string
  action: string
  outcome: string
  original: string
}

function parseUserStory(story: string): ParsedUserStory | null {
  // More flexible regex that handles optional commas, alternate phrasings, and articles (a/an/the)
  const regex = /As\s+(?:a|an|the)\s+(.+?)[,;]?\s+I\s+want\s+to\s+(.+?)[,;]?\s+(?:so\s+that|to|in\s+order\s+to)\s+(.+)/i
  const match = story.match(regex)

  if (match) {
    return {
      role: match[1].trim(),
      action: match[2].trim(),
      outcome: match[3].trim(),
      original: story,
    }
  }
  return null
}

export function UserStoryInput({ value, onChange, errors }: UserStoryInputProps) {
  const { suggestionsEnabled, getSuggestions, isLoading } = useSuggestionContext()
  const [suggestions, setSuggestions] = useState<string[]>([])
  const [selectedIndex, setSelectedIndex] = useState<number | null>(null)
  const [showSuggestions, setShowSuggestions] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // Reset selection when user manually edits fields
  useEffect(() => {
    setSelectedIndex(null)
  }, [value.role, value.action, value.outcome])

  const updateField = (field: keyof UserStory, fieldValue: string) => {
    onChange({ ...value, [field]: fieldValue })
  }

  const handleGetSuggestions = async () => {
    setShowSuggestions(true)
    setError(null)
    try {
      const results = await getSuggestions('user_stories')
      setSuggestions(results)
    } catch (err) {
      setError('Failed to load suggestions. Please try again.')
      setSuggestions([])
    }
  }

  const handleUseSuggestion = () => {
    if (selectedIndex === null || selectedIndex < 0 || selectedIndex >= suggestions.length) return

    const parsed = parseUserStory(suggestions[selectedIndex])
    if (parsed) {
      onChange({
        role: parsed.role,
        action: parsed.action,
        outcome: parsed.outcome,
      })
      setShowSuggestions(false)
      setSelectedIndex(null)
      setError(null)
    } else {
      setError('Could not parse the selected suggestion. Please try another suggestion or enter your user story manually.')
    }
  }

  const handleSkip = () => {
    setShowSuggestions(false)
    setSelectedIndex(null)
    setError(null)
  }

  const handleGetMore = async () => {
    setError(null)
    try {
      const results = await getSuggestions('user_stories')
      setSuggestions(results)
      setSelectedIndex(null)
    } catch (err) {
      setError('Failed to load suggestions. Please try again.')
      setSuggestions([])
    }
  }

  return (
    <div className="space-y-4">
      {/* Suggestion Button */}
      {suggestionsEnabled && !showSuggestions && (
        <button
          type="button"
          onClick={handleGetSuggestions}
          disabled={isLoading}
          className="w-full py-3 px-4 bg-gradient-to-r from-blue-50 to-purple-50 border-2 border-dashed border-blue-300 rounded-lg hover:from-blue-100 hover:to-purple-100 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          aria-label="Get AI-powered user story suggestions"
        >
          {isLoading ? (
            <span className="flex items-center justify-center gap-2 text-blue-700">
              <span className="animate-spin" aria-hidden="true">🔄</span>
              <span>Generating suggestions...</span>
            </span>
          ) : (
            <span className="flex items-center justify-center gap-2 text-blue-700 font-medium">
              <span className="sr-only">Get suggestions based on your project description</span>
              <span aria-hidden="true">✨</span>
              <span>Get suggestions based on your project description</span>
            </span>
          )}
        </button>
      )}

      {/* Error State */}
      {showSuggestions && error && (
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
              aria-label="Retry loading suggestions"
            >
              {isLoading ? 'Loading...' : 'Try again'}
            </button>
            <button
              type="button"
              onClick={handleSkip}
              className="py-2 px-4 bg-white border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50"
              aria-label="Dismiss error and enter manually"
            >
              Dismiss
            </button>
          </div>
        </div>
      )}

      {/* Empty Suggestions State */}
      {showSuggestions && !error && !isLoading && suggestions.length === 0 && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <p className="text-sm text-yellow-800">
            <span aria-hidden="true">💭</span> No suggestions available at this time.
          </p>
          <p className="text-xs text-yellow-600 mt-1">
            Try providing more details in your project description, or enter your user story manually below.
          </p>
          <div className="flex gap-2 mt-3">
            <button
              type="button"
              onClick={handleGetMore}
              disabled={isLoading}
              className="py-2 px-4 bg-white border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
              aria-label="Try getting suggestions again"
            >
              Try again
            </button>
            <button
              type="button"
              onClick={handleSkip}
              className="py-2 px-4 bg-white border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50"
              aria-label="Continue entering user story manually"
            >
              Continue manually
            </button>
          </div>
        </div>
      )}

      {/* Suggestions Display */}
      {showSuggestions && !error && suggestions.length > 0 && (
        <div
          className="bg-blue-50 border border-blue-200 rounded-lg p-4 space-y-3"
          onKeyDown={(e) => {
            if (e.key === 'Enter' && selectedIndex !== null) {
              e.preventDefault()
              handleUseSuggestion()
            }
          }}
        >
          <p className="text-sm font-medium text-blue-900">
            <span className="sr-only">Suggested user stories</span>
            <span aria-hidden="true">💡</span> Suggested user stories:
          </p>

          <div className="space-y-2">
            {suggestions.map((suggestion, index) => {
              const parsed = parseUserStory(suggestion)

              // Handle unparseable suggestions
              if (!parsed) {
                return (
                  <div key={index} className="p-3 bg-yellow-50 border-2 border-yellow-200 rounded-lg">
                    <p className="text-sm text-yellow-800">
                      <span aria-hidden="true">⚠️</span> {suggestion}
                    </p>
                    <p className="text-xs text-yellow-600 mt-1">
                      Could not parse this suggestion. Please try "Get more" for better results.
                    </p>
                  </div>
                )
              }

              return (
                <label
                  key={index}
                  className={`block p-3 bg-white border-2 rounded-lg cursor-pointer transition-all ${
                    selectedIndex === index
                      ? 'border-blue-500 bg-blue-50'
                      : 'border-gray-200 hover:border-blue-300'
                  }`}
                >
                  <input
                    type="radio"
                    name="user-story-suggestion"
                    checked={selectedIndex === index}
                    onChange={() => setSelectedIndex(index)}
                    className="mr-2"
                    aria-label={`Select suggestion: ${suggestion}`}
                  />
                  <span className="text-sm text-gray-900">{suggestion}</span>
                </label>
              )
            })}
          </div>

          <div className="flex gap-2 pt-2">
            <button
              type="button"
              onClick={handleUseSuggestion}
              disabled={selectedIndex === null || isLoading}
              className="flex-1 py-2 px-4 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed font-medium"
              aria-label="Use selected user story suggestion"
            >
              Use suggestion
            </button>
            <button
              type="button"
              onClick={handleGetMore}
              disabled={isLoading}
              className="py-2 px-4 bg-white border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
              aria-label="Get more user story suggestions"
            >
              Get more
            </button>
            <button
              type="button"
              onClick={handleSkip}
              className="py-2 px-4 bg-white border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50"
              aria-label="Skip suggestions and enter manually"
            >
              Skip
            </button>
          </div>
        </div>
      )}

      {/* Manual Input Fields */}
      <div className="flex items-center gap-2 text-lg text-gray-600">
        <span>As</span>
        <input
          type="text"
          value={value.role}
          onChange={(e) => updateField('role', e.target.value)}
          className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          placeholder="a developer"
        />
      </div>
      {errors?.role && (
        <p className="text-sm text-red-600">{errors.role.message}</p>
      )}

      <div className="flex items-center gap-2 text-lg text-gray-600">
        <span>I want to</span>
        <input
          type="text"
          value={value.action}
          onChange={(e) => updateField('action', e.target.value)}
          className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          placeholder="quickly bootstrap new projects"
        />
      </div>
      {errors?.action && (
        <p className="text-sm text-red-600">{errors.action.message}</p>
      )}

      <div className="flex items-center gap-2 text-lg text-gray-600">
        <span>So that</span>
        <input
          type="text"
          value={value.outcome}
          onChange={(e) => updateField('outcome', e.target.value)}
          className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          placeholder="I can focus on building features"
        />
      </div>
      {errors?.outcome && (
        <p className="text-sm text-red-600">{errors.outcome.message}</p>
      )}
    </div>
  )
}
