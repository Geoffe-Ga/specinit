interface SuggestionActionsProps {
  selectedCount: number
  isLoading: boolean
  onAddSelected: () => void
  onGetMore: () => void
  onSkipAll: () => void
}

export function SuggestionActions({
  selectedCount,
  isLoading,
  onAddSelected,
  onGetMore,
  onSkipAll,
}: SuggestionActionsProps) {
  return (
    <div className="flex gap-2 pt-2">
      <button
        type="button"
        onClick={onAddSelected}
        disabled={selectedCount === 0 || isLoading}
        className="flex-1 py-2 px-4 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed font-medium"
        aria-label={`Add ${selectedCount} selected features`}
      >
        {isLoading ? (
          <span className="flex items-center justify-center gap-2">
            <span className="animate-spin" aria-hidden="true">🔄</span>
            <span>Loading...</span>
          </span>
        ) : (
          `✓ Add selected (${selectedCount})`
        )}
      </button>
      <button
        type="button"
        onClick={onGetMore}
        disabled={isLoading}
        className="py-2 px-4 bg-white border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
        aria-label="Get more feature suggestions"
      >
        {isLoading ? 'Loading...' : 'Get more'}
      </button>
      <button
        type="button"
        onClick={onSkipAll}
        className="py-2 px-4 bg-white border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50"
      >
        Skip all
      </button>
    </div>
  )
}
