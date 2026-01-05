import { useState, useEffect } from 'react'
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

  // Auto-trigger suggestions when component mounts if enabled
  useEffect(() => {
    if (suggestionsEnabled && !showSuggestions && suggestions.length === 0) {
      handleGetSuggestions()
    }
  }, [suggestionsEnabled]) // eslint-disable-line react-hooks/exhaustive-deps

  const handleGetSuggestions = async () => {
    setShowSuggestions(true)
    const results = await getSuggestions('tech_stack')
    setSuggestions(results)
  }

  const handleAddSuggestion = (suggestion: string) => {
    // Try to categorize the suggestion based on TECH_OPTIONS
    let category: keyof TechStack | null = null

    for (const [cat, options] of Object.entries(TECH_OPTIONS)) {
      if (options.some((opt) => suggestion.toLowerCase().includes(opt.toLowerCase()))) {
        category = cat as keyof TechStack
        break
      }
    }

    // Default to tools if we can't categorize
    if (!category) category = 'tools'

    // Add to appropriate category if not already there
    if (!value[category].includes(suggestion)) {
      onChange({ ...value, [category]: [...value[category], suggestion] })
    }
  }

  const handleSkipAll = () => {
    setShowSuggestions(false)
  }

  const handleGetMore = async () => {
    const results = await getSuggestions('tech_stack')
    setSuggestions(results)
  }

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
      {/* Suggestions Display */}
      {suggestionsEnabled && showSuggestions && suggestions.length > 0 && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 space-y-3">
          <p className="text-sm font-medium text-blue-900">
            💡 Recommended technologies for your project:
          </p>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
            {suggestions.map((suggestion, index) => {
              const isAdded =
                value.frontend.includes(suggestion) ||
                value.backend.includes(suggestion) ||
                value.database.includes(suggestion) ||
                value.tools.includes(suggestion)

              return (
                <button
                  key={index}
                  type="button"
                  onClick={() => handleAddSuggestion(suggestion)}
                  disabled={isAdded}
                  className={`p-3 text-left text-sm rounded-lg border-2 transition-all ${
                    isAdded
                      ? 'border-green-500 bg-green-50 text-green-900'
                      : 'border-gray-200 bg-white hover:border-blue-300'
                  }`}
                >
                  {isAdded ? (
                    <span className="flex items-center gap-2">
                      <span className="text-green-600">✓</span> {suggestion}
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
            >
              Get more
            </button>
            <button
              type="button"
              onClick={handleSkipAll}
              className="py-2 px-4 bg-white border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50"
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
