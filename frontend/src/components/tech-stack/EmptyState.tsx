interface EmptyStateProps {
  onSkipAll: () => void
}

export function EmptyState({ onSkipAll }: EmptyStateProps) {
  return (
    <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
      <p className="text-sm text-yellow-800">
        <span aria-hidden="true">⚠️</span> No suggestions available at this time.
      </p>
      <p className="text-xs text-yellow-600 mt-1">Please choose technologies manually below or try again.</p>
      <button
        type="button"
        onClick={onSkipAll}
        className="mt-2 py-2 px-4 bg-white border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50"
        aria-label="Skip suggestions and continue choosing technologies manually"
      >
        Continue manually
      </button>
    </div>
  )
}
