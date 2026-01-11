import { SuggestionActions } from './SuggestionActions'

interface SuggestionListProps {
  suggestions: string[]
  selectedIndices: number[]
  isLoading: boolean
  onToggle: (index: number) => void
  onAddSelected: () => void
  onGetMore: () => void
  onSkipAll: () => void
}

export function SuggestionList({
  suggestions,
  selectedIndices,
  isLoading,
  onToggle,
  onAddSelected,
  onGetMore,
  onSkipAll,
}: SuggestionListProps) {
  return (
    <>
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 space-y-3">
        <p className="text-sm font-medium text-blue-900">
          <span className="sr-only">Suggested features based on your user story</span>
          <span aria-hidden="true">💡</span> Suggested features (based on your user story):
        </p>

        <div className="space-y-2">
          {suggestions.map((suggestion, index) => (
            <label
              key={index}
              className={`flex items-start gap-3 p-3 bg-white border-2 rounded-lg cursor-pointer transition-all ${
                selectedIndices.includes(index)
                  ? 'border-blue-500 bg-blue-50'
                  : 'border-gray-200 hover:border-blue-300'
              }`}
            >
              <input
                type="checkbox"
                checked={selectedIndices.includes(index)}
                onChange={() => onToggle(index)}
                className="mt-0.5"
                aria-label={`Select feature: ${suggestion}`}
              />
              <span className="text-sm text-gray-900 flex-1">{suggestion}</span>
            </label>
          ))}
        </div>

        <SuggestionActions
          selectedCount={selectedIndices.length}
          isLoading={isLoading}
          onAddSelected={onAddSelected}
          onGetMore={onGetMore}
          onSkipAll={onSkipAll}
        />
      </div>

      <div className="text-center">
        <p className="text-sm text-gray-600">Or add your own:</p>
      </div>
    </>
  )
}
