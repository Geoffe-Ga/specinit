import { Plus } from 'lucide-react'

import { useFeatureSuggestions } from '../hooks/useFeatureSuggestions'

import { FeatureInput } from './FeatureInput'
import { SuggestionPanel } from './SuggestionPanel'

interface FeatureListProps {
  features: string[]
  onChange: (features: string[]) => void
  error?: string
}

const MAX_FEATURES = 20
const MAX_FEATURE_LENGTH = 2000

export function FeatureList({ features, onChange, error }: FeatureListProps) {
  const {
    suggestions,
    selectedIndices,
    showSuggestions,
    suggestionError,
    handleGetSuggestions,
    handleGetMore,
    handleAddSelected,
    handleSkipAll,
    toggleSelection,
  } = useFeatureSuggestions()

  const addFeature = () => {
    if (features.length < MAX_FEATURES) {
      onChange([...features, ''])
    }
  }

  const removeFeature = (index: number) => {
    if (features.length > 1) {
      onChange(features.filter((_, i) => i !== index))
    }
  }

  const updateFeature = (index: number, value: string) => {
    const newFeatures = [...features]
    newFeatures[index] = value
    onChange(newFeatures)
  }

  return (
    <div className="space-y-4">
      <SuggestionPanel
        suggestions={suggestions}
        selectedIndices={selectedIndices}
        showSuggestions={showSuggestions}
        suggestionError={suggestionError}
        onGetSuggestions={handleGetSuggestions}
        onGetMore={handleGetMore}
        onAddSelected={() => handleAddSelected(features, onChange, MAX_FEATURES)}
        onSkipAll={handleSkipAll}
        onToggleSelection={toggleSelection}
      />

      {features.map((feature, index) => (
        <FeatureInput
          key={index}
          feature={feature}
          index={index}
          onUpdate={(value) => updateFeature(index, value)}
          onRemove={() => removeFeature(index)}
          canRemove={features.length > 1}
          maxLength={MAX_FEATURE_LENGTH}
        />
      ))}

      <button
        type="button"
        onClick={addFeature}
        disabled={features.length >= MAX_FEATURES}
        className="flex items-center gap-2 px-4 py-2 text-blue-600 border border-blue-600 rounded-md hover:bg-blue-50 disabled:opacity-50 disabled:cursor-not-allowed"
        aria-label={`Add feature (${features.length} of ${MAX_FEATURES} features used)`}
      >
        <Plus className="w-5 h-5" aria-hidden="true" />
        Add Feature ({features.length}/{MAX_FEATURES})
      </button>

      {error && <p className="mt-2 text-sm text-red-600">{error}</p>}
    </div>
  )
}
