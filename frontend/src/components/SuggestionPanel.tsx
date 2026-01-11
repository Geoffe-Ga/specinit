import { useSuggestionContext } from '../contexts/SuggestionContext'

import { SuggestionEmptyState } from './SuggestionEmptyState'
import { SuggestionErrorState } from './SuggestionErrorState'
import { SuggestionList } from './SuggestionList'
import { SuggestionLoadingState } from './SuggestionLoadingState'

interface SuggestionPanelProps {
  suggestions: string[]
  selectedIndices: number[]
  showSuggestions: boolean
  suggestionError: string | null
  onGetSuggestions: () => void
  onGetMore: () => void
  onAddSelected: () => void
  onSkipAll: () => void
  onToggleSelection: (index: number) => void
}

export function SuggestionPanel({
  suggestions,
  selectedIndices,
  showSuggestions,
  suggestionError,
  onGetSuggestions,
  onGetMore,
  onAddSelected,
  onSkipAll,
  onToggleSelection,
}: SuggestionPanelProps) {
  const { suggestionsEnabled, isLoading } = useSuggestionContext()

  if (!suggestionsEnabled || !showSuggestions) {
    return null
  }

  if (isLoading && suggestions.length === 0) {
    return <SuggestionLoadingState />
  }

  if (suggestionError) {
    return (
      <SuggestionErrorState
        error={suggestionError}
        isLoading={isLoading}
        onRetry={onGetSuggestions}
        onSkip={onSkipAll}
      />
    )
  }

  if (!isLoading && suggestions.length === 0) {
    return <SuggestionEmptyState onSkip={onSkipAll} />
  }

  return (
    <SuggestionList
      suggestions={suggestions}
      selectedIndices={selectedIndices}
      isLoading={isLoading}
      onToggle={onToggleSelection}
      onAddSelected={onAddSelected}
      onGetMore={onGetMore}
      onSkipAll={onSkipAll}
    />
  )
}
