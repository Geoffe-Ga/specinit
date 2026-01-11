interface SuggestionButtonProps {
  suggestion: string
  isAdded: boolean
  onAdd: (suggestion: string) => void
}

export function SuggestionButton({ suggestion, isAdded, onAdd }: SuggestionButtonProps) {
  return (
    <button
      type="button"
      onClick={() => onAdd(suggestion)}
      disabled={isAdded}
      className={`p-3 text-left text-sm rounded-lg border-2 transition-all ${
        isAdded
          ? 'border-green-500 bg-green-50 text-green-900'
          : 'border-gray-200 bg-white hover:border-blue-300'
      }`}
      aria-label={isAdded ? `${suggestion} - already added` : `Add ${suggestion}`}
    >
      {isAdded ? (
        <span className="flex items-center gap-2">
          <span className="text-green-600" aria-hidden="true">
            ✓
          </span>{' '}
          {suggestion}
        </span>
      ) : (
        suggestion
      )}
    </button>
  )
}
