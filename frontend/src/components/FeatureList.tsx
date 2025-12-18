import { X, Plus } from 'lucide-react'

interface FeatureListProps {
  features: string[]
  onChange: (features: string[]) => void
  error?: string
}

const MAX_FEATURES = 20
const MAX_FEATURE_LENGTH = 2000 // characters

export function FeatureList({ features, onChange, error }: FeatureListProps) {
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

  return (
    <div className="space-y-4">
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
            >
              <X className="w-5 h-5" />
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
      >
        <Plus className="w-5 h-5" />
        Add Feature ({features.length}/{MAX_FEATURES})
      </button>

      {error && <p className="mt-2 text-sm text-red-600">{error}</p>}
    </div>
  )
}
