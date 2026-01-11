import type { TechStack } from '../../types'

import { EmptyState } from './EmptyState'
import { ErrorState } from './ErrorState'
import { LoadingState } from './LoadingState'
import { SuggestionList } from './SuggestionList'

interface SuggestionsPanelProps {
  suggestionsEnabled: boolean
  showSuggestions: boolean
  isLoading: boolean
  error: string | null
  suggestions: string[]
  value: TechStack
  onGetSuggestions: () => void
  onAddSuggestion: (suggestion: string) => void
  onSkipAll: () => void
}

function SuggestionsContent({
  isLoading,
  error,
  suggestions,
  value,
  onGetSuggestions,
  onAddSuggestion,
  onSkipAll,
}: Omit<SuggestionsPanelProps, 'suggestionsEnabled' | 'showSuggestions'>) {
  if (isLoading && suggestions.length === 0) return <LoadingState />
  if (error) return <ErrorState error={error} isLoading={isLoading} onRetry={onGetSuggestions} onDismiss={onSkipAll} />
  if (suggestions.length === 0) return <EmptyState onSkipAll={onSkipAll} />

  return (
    <>
      <SuggestionList
        suggestions={suggestions}
        value={value}
        isLoading={isLoading}
        onAdd={onAddSuggestion}
        onGetMore={onGetSuggestions}
        onSkip={onSkipAll}
      />
      <div className="text-center">
        <p className="text-sm text-gray-600">Or choose manually:</p>
      </div>
    </>
  )
}

export function SuggestionsPanel({
  suggestionsEnabled,
  showSuggestions,
  isLoading,
  error,
  suggestions,
  value,
  onGetSuggestions,
  onAddSuggestion,
  onSkipAll,
}: SuggestionsPanelProps) {
  if (!suggestionsEnabled || !showSuggestions) return null

  return (
    <SuggestionsContent
      isLoading={isLoading}
      error={error}
      suggestions={suggestions}
      value={value}
      onGetSuggestions={onGetSuggestions}
      onAddSuggestion={onAddSuggestion}
      onSkipAll={onSkipAll}
    />
  )
}
