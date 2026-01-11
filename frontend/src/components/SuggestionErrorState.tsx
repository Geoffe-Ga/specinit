interface SuggestionErrorStateProps {
  error: string
  isLoading: boolean
  onRetry: () => void
  onSkip: () => void
}

export function SuggestionErrorState({
  error,
  isLoading,
  onRetry,
  onSkip,
}: SuggestionErrorStateProps) {
  return (
    <div className="bg-red-50 border border-red-200 rounded-lg p-4">
      <div className="flex items-start gap-2">
        <span className="text-red-600" aria-hidden="true">❌</span>
        <div className="flex-1">
          <p className="text-sm font-medium text-red-800">Failed to fetch suggestions</p>
          <p className="text-xs text-red-600 mt-1">{error}</p>
          <p className="text-xs text-red-600 mt-1">
            Check your internet connection and API key configuration.
          </p>
        </div>
      </div>
      <div className="flex gap-2 mt-3">
        <button
          type="button"
          onClick={onRetry}
          disabled={isLoading}
          className="py-2 px-4 bg-white border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
          aria-label="Retry fetching suggestions"
        >
          {isLoading ? 'Retrying...' : 'Try again'}
        </button>
        <button
          type="button"
          onClick={onSkip}
          className="py-2 px-4 bg-white border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50"
          aria-label="Dismiss error and continue manually"
        >
          Continue manually
        </button>
      </div>
    </div>
  )
}
