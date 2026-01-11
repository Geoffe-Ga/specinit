interface SuggestionEmptyStateProps {
  onSkip: () => void
}

export function SuggestionEmptyState({ onSkip }: SuggestionEmptyStateProps) {
  return (
    <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
      <p className="text-sm text-yellow-800">
        <span aria-hidden="true">⚠️</span> No suggestions available at this time.
      </p>
      <p className="text-xs text-yellow-600 mt-1">
        Please try again or add your features manually below.
      </p>
      <button
        type="button"
        onClick={onSkip}
        className="mt-2 py-2 px-4 bg-white border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50"
      >
        Continue manually
      </button>
    </div>
  )
}
