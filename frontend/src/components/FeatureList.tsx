import { useState, useEffect } from 'react'
import { X, Plus } from 'lucide-react'
import { useSuggestionContext } from '../contexts/SuggestionContext'

interface FeatureListProps {
  features: string[]
  onChange: (features: string[]) => void
  error?: string
}

const MAX_FEATURES = 20
const MAX_FEATURE_LENGTH = 2000 // characters

export function FeatureList({ features, onChange, error }: FeatureListProps) {
  const { suggestionsEnabled, getSuggestions, isLoading } = useSuggestionContext()
  const [suggestions, setSuggestions] = useState<string[]>([])
  const [selectedIndices, setSelectedIndices] = useState<number[]>([])
  const [showSuggestions, setShowSuggestions] = useState(false)

  // Auto-trigger suggestions when component mounts if enabled
  useEffect(() => {
    if (suggestionsEnabled && !showSuggestions && suggestions.length === 0) {
      handleGetSuggestions()
    }
  }, [suggestionsEnabled]) // eslint-disable-line react-hooks/exhaustive-deps

  const addFeature = () => {
    if (features.length < MAX_FEATURES) {
      onChange([...features, ''])
    }
  }

  const removeFeature = (index: number) => {
    // Don't allow removing the last feature if there's only one
    if (features.length > 1) {
      onChange(features.filter((_, i) => i !== index))
    }
  }

  const updateFeature = (index: number, value: string) => {
    const newFeatures = [...features]
    newFeatures[index] = value
    onChange(newFeatures)
  }

  const handleGetSuggestions = async () => {
    setShowSuggestions(true)
    const results = await getSuggestions('features')
    setSuggestions(results)
    setSelectedIndices([])
  }

  const toggleSelection = (index: number) => {
    setSelectedIndices((prev) =>
      prev.includes(index) ? prev.filter((i) => i !== index) : [...prev, index]
    )
  }

  const handleAddSelected = () => {
    const selectedFeatures = selectedIndices.map((i) => suggestions[i])
    // Filter out empty features and add selected suggestions
    const nonEmptyFeatures = features.filter((f) => f.trim())
    const newFeatures = [...nonEmptyFeatures, ...selectedFeatures].slice(0, MAX_FEATURES)
    onChange(newFeatures)
    setShowSuggestions(false)
    setSelectedIndices([])
  }

  const handleSkipAll = () => {
    setShowSuggestions(false)
    setSelectedIndices([])
  }

  const handleGetMore = async () => {
    const results = await getSuggestions('features')
    setSuggestions(results)
    setSelectedIndices([])
  }

  return (
    <div className="space-y-4">
      {/* Suggestions Display */}
      {suggestionsEnabled && showSuggestions && suggestions.length > 0 && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 space-y-3">
          <p className="text-sm font-medium text-blue-900">
            💡 Suggested features (based on your user story):
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
                  onChange={() => toggleSelection(index)}
                  className="mt-0.5"
                />
                <span className="text-sm text-gray-900 flex-1">{suggestion}</span>
              </label>
            ))}
          </div>

          <div className="flex gap-2 pt-2">
            <button
              type="button"
              onClick={handleAddSelected}
              disabled={selectedIndices.length === 0 || isLoading}
              className="flex-1 py-2 px-4 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed font-medium"
            >
              ✓ Add selected ({selectedIndices.length})
            </button>
            <button
              type="button"
              onClick={handleGetMore}
              disabled={isLoading}
              className="py-2 px-4 bg-white border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Get more
            </button>
            <button
              type="button"
              onClick={handleSkipAll}
              className="py-2 px-4 bg-white border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50"
            >
              Skip all
            </button>
          </div>
        </div>
      )}

      {/* Or add your own label */}
      {suggestionsEnabled && showSuggestions && suggestions.length > 0 && (
        <div className="text-center">
          <p className="text-sm text-gray-600">Or add your own:</p>
        </div>
      )}

      {/* Feature fields */}
      {features.map((feature, index) => {
        const wordCount = feature.trim() ? feature.trim().split(/\s+/).filter(w => w).length : 0
        return (
          <div key={index} className="relative">
            <div className="flex items-start gap-2">
              <div className="flex-1">
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Feature {index + 1}
                </label>
                <textarea
                  value={feature}
                  onChange={(e) => updateFeature(index, e.target.value)}
                  maxLength={MAX_FEATURE_LENGTH}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-y min-h-[80px]"
                  placeholder="Describe this feature (1-2 words for simple features, or write detailed requirements)..."
                />
                <div className="mt-1 flex items-center justify-between text-xs text-gray-500">
                  <span>{feature.length} / {MAX_FEATURE_LENGTH} characters</span>
                  <span>{wordCount} word{wordCount !== 1 ? 's' : ''}</span>
                </div>
              </div>
            <button
              type="button"
              onClick={() => removeFeature(index)}
              disabled={features.length === 1}
              className="mt-7 p-2 text-gray-400 hover:text-red-500 disabled:opacity-50 disabled:cursor-not-allowed"
              title={features.length === 1 ? "Cannot remove the last feature" : "Remove feature"}
              aria-label={features.length === 1 ? "Cannot remove the last feature" : `Remove feature ${index + 1}`}
            >
              <X className="w-5 h-5" aria-hidden="true" />
            </button>
          </div>
        </div>
        )
      })}

      {/* Add feature button */}
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
