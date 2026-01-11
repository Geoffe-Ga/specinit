import type { TechStack } from '../../types'

import { SuggestionButton } from './SuggestionButton'

interface SuggestionListProps {
  suggestions: string[]
  value: TechStack
  isLoading: boolean
  onAdd: (suggestion: string) => void
  onGetMore: () => void
  onSkip: () => void
}

export function SuggestionList({ suggestions, value, isLoading, onAdd, onGetMore, onSkip }: SuggestionListProps) {
  return (
    <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 space-y-3">
      <p className="text-sm font-medium text-blue-900">
        <span className="sr-only">Recommended technologies for your project</span>
        <span aria-hidden="true">💡</span> Recommended technologies for your project:
      </p>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
        {suggestions.map((suggestion) => {
          const isAdded = Object.values(value).some((arr) => arr.includes(suggestion))
          return <SuggestionButton key={suggestion} suggestion={suggestion} isAdded={isAdded} onAdd={onAdd} />
        })}
      </div>

      <div className="flex gap-2 pt-2">
        <button
          type="button"
          onClick={onGetMore}
          disabled={isLoading}
          className="py-2 px-4 bg-white border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
          aria-label="Get more tech stack suggestions"
        >
          {isLoading ? 'Loading...' : 'Get more'}
        </button>
        <button
          type="button"
          onClick={onSkip}
          className="py-2 px-4 bg-white border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50"
          aria-label="Skip suggestions and choose manually"
        >
          Skip all
        </button>
      </div>
    </div>
  )
}
