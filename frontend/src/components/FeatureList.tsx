import { useState } from 'react'
import { X, Plus } from 'lucide-react'

interface FeatureListProps {
  features: string[]
  onChange: (features: string[]) => void
  error?: string
}

const SUGGESTIONS = [
  'User authentication',
  'Dark mode',
  'Offline support',
  'Push notifications',
  'Search functionality',
  'User profiles',
  'Data export',
  'Admin dashboard',
]

export function FeatureList({ features, onChange, error }: FeatureListProps) {
  const [newFeature, setNewFeature] = useState('')

  const addFeature = () => {
    if (newFeature.trim() && features.length < 10) {
      onChange([...features, newFeature.trim()])
      setNewFeature('')
    }
  }

  const removeFeature = (index: number) => {
    onChange(features.filter((_, i) => i !== index))
  }

  const addSuggestion = (suggestion: string) => {
    if (!features.includes(suggestion) && features.length < 10) {
      onChange([...features, suggestion])
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      e.preventDefault()
      addFeature()
    }
  }

  const availableSuggestions = SUGGESTIONS.filter((s) => !features.includes(s))

  return (
    <div>
      {/* Feature input */}
      <div className="flex gap-2 mb-4">
        <input
          type="text"
          value={newFeature}
          onChange={(e) => setNewFeature(e.target.value)}
          onKeyDown={handleKeyDown}
          className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          placeholder="Add a feature..."
          disabled={features.length >= 10}
        />
        <button
          type="button"
          onClick={addFeature}
          disabled={!newFeature.trim() || features.length >= 10}
          className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <Plus className="w-5 h-5" />
        </button>
      </div>

      {/* Feature list */}
      {features.length > 0 && (
        <ul className="space-y-2 mb-4">
          {features.map((feature, index) => (
            <li
              key={index}
              className="flex items-center justify-between px-4 py-2 bg-gray-50 rounded-md"
            >
              <span>{feature}</span>
              <button
                type="button"
                onClick={() => removeFeature(index)}
                className="text-gray-400 hover:text-red-500"
              >
                <X className="w-4 h-4" />
              </button>
            </li>
          ))}
        </ul>
      )}

      {/* Suggestions */}
      {availableSuggestions.length > 0 && features.length < 10 && (
        <div>
          <p className="text-sm text-gray-600 mb-2">Suggestions:</p>
          <div className="flex flex-wrap gap-2">
            {availableSuggestions.slice(0, 4).map((suggestion) => (
              <button
                key={suggestion}
                type="button"
                onClick={() => addSuggestion(suggestion)}
                className="px-3 py-1 text-sm bg-gray-100 text-gray-700 rounded-full hover:bg-gray-200"
              >
                + {suggestion}
              </button>
            ))}
          </div>
        </div>
      )}

      {error && <p className="mt-2 text-sm text-red-600">{error}</p>}
      <p className="mt-2 text-sm text-gray-500">{features.length}/10 features</p>
    </div>
  )
}
