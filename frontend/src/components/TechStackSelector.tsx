import { useCallback, useEffect, useRef, useState } from 'react'

import { useSuggestionContext } from '../contexts/SuggestionContext'
import { TECH_OPTIONS, type TechStack } from '../types'

import { SuggestionsPanel } from './tech-stack/SuggestionsPanel'

interface TechStackSelectorProps {
  value: TechStack
  onChange: (techStack: TechStack) => void
  platforms: string[]
}

const SELECTED_CLASS = 'bg-blue-600 text-white'
const UNSELECTED_CLASS = 'bg-gray-100 text-gray-700 hover:bg-gray-200'
const ERROR_MESSAGE = 'Failed to load suggestions. Please try again.'

interface CategorySectionProps {
  title: string
  category: keyof TechStack
  options: string[]
  selectedOptions: string[]
  onToggle: (category: keyof TechStack, option: string) => void
}

function CategorySection({ title, category, options, selectedOptions, onToggle }: CategorySectionProps) {
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

function categorizeSuggestion(suggestion: string): keyof TechStack {
  for (const [cat, options] of Object.entries(TECH_OPTIONS)) {
    const match = options.some((opt) => suggestion.toLowerCase().includes(opt.toLowerCase()))
    if (match) return cat as keyof TechStack
  }
  return 'tools'
}

function useTechStackSuggestions(value: TechStack, onChange: (techStack: TechStack) => void) {
  const { suggestionsEnabled, getSuggestions, isLoading } = useSuggestionContext()
  const [suggestions, setSuggestions] = useState<string[]>([])
  const [showSuggestions, setShowSuggestions] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const hasFetchedRef = useRef(false)
  const isMountedRef = useRef(true)

  useEffect(() => () => { isMountedRef.current = false }, [])
  useEffect(() => { if (!suggestionsEnabled) hasFetchedRef.current = false }, [suggestionsEnabled])

  const handleGetSuggestions = useCallback(async () => {
    setShowSuggestions(true)
    setError(null)
    try {
      const results = await getSuggestions('tech_stack')
      if (isMountedRef.current) setSuggestions(results)
    } catch (err) {
      console.error('Failed to get tech stack suggestions:', err)
      if (isMountedRef.current) {
        setError(ERROR_MESSAGE)
        setSuggestions([])
      }
    }
  }, [getSuggestions])

  useEffect(() => {
    const shouldFetch = suggestionsEnabled && !showSuggestions && suggestions.length === 0 && !hasFetchedRef.current
    if (shouldFetch) {
      hasFetchedRef.current = true
      setShowSuggestions(true)
      setError(null)
      getSuggestions('tech_stack')
        .then((results) => { if (isMountedRef.current) setSuggestions(results) })
        .catch((err) => {
          console.error('Failed to auto-trigger tech stack suggestions:', err)
          if (isMountedRef.current) {
            setError(ERROR_MESSAGE)
            setSuggestions([])
          }
        })
    }
  }, [suggestionsEnabled, showSuggestions, suggestions.length, getSuggestions])

  const handleAddSuggestion = useCallback(
    (suggestion: string) => {
      const alreadyExists = Object.values(value).some((arr) => arr.includes(suggestion))
      if (alreadyExists) return

      const category = categorizeSuggestion(suggestion)
      onChange({ ...value, [category]: [...value[category], suggestion] })
    },
    [value, onChange]
  )

  const handleSkipAll = () => {
    setShowSuggestions(false)
    setError(null)
  }

  return {
    suggestions,
    showSuggestions,
    error,
    isLoading,
    handleGetSuggestions,
    handleAddSuggestion,
    handleSkipAll,
  }
}

interface CategoryListProps {
  value: TechStack
  platforms: string[]
  onToggle: (category: keyof TechStack, option: string) => void
}

function CategoryList({ value, platforms, onToggle }: CategoryListProps) {
  const showFrontend = platforms.some((p) => ['web', 'ios', 'android', 'desktop'].includes(p))
  const showBackend = !platforms.every((p) => p === 'cli')

  return (
    <>
      {showFrontend && (
        <CategorySection
          title="Frontend"
          category="frontend"
          options={TECH_OPTIONS.frontend}
          selectedOptions={value.frontend}
          onToggle={onToggle}
        />
      )}

      {showBackend && (
        <CategorySection
          title="Backend"
          category="backend"
          options={TECH_OPTIONS.backend}
          selectedOptions={value.backend}
          onToggle={onToggle}
        />
      )}

      <CategorySection
        title="Database"
        category="database"
        options={TECH_OPTIONS.database}
        selectedOptions={value.database}
        onToggle={onToggle}
      />

      <CategorySection
        title="Tools"
        category="tools"
        options={TECH_OPTIONS.tools}
        selectedOptions={value.tools}
        onToggle={onToggle}
      />
    </>
  )
}

export function TechStackSelector({ value, onChange, platforms }: TechStackSelectorProps) {
  const { suggestions, showSuggestions, error, isLoading, handleGetSuggestions, handleAddSuggestion, handleSkipAll } =
    useTechStackSuggestions(value, onChange)
  const { suggestionsEnabled } = useSuggestionContext()

  const toggleOption = (category: keyof TechStack, option: string) => {
    const current = value[category]
    const updated = current.includes(option) ? current.filter((o) => o !== option) : [...current, option]
    onChange({ ...value, [category]: updated })
  }

  return (
    <div className="space-y-6">
      <SuggestionsPanel
        suggestionsEnabled={suggestionsEnabled}
        showSuggestions={showSuggestions}
        isLoading={isLoading}
        error={error}
        suggestions={suggestions}
        value={value}
        onGetSuggestions={handleGetSuggestions}
        onAddSuggestion={handleAddSuggestion}
        onSkipAll={handleSkipAll}
      />

      <CategoryList value={value} platforms={platforms} onToggle={toggleOption} />
    </div>
  )
}
