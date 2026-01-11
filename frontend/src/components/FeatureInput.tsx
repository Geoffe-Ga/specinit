import { X } from 'lucide-react'

interface FeatureInputProps {
  feature: string
  index: number
  onUpdate: (value: string) => void
  onRemove: () => void
  canRemove: boolean
  maxLength: number
}

export function FeatureInput({
  feature,
  index,
  onUpdate,
  onRemove,
  canRemove,
  maxLength,
}: FeatureInputProps) {
  const wordCount = feature.trim()
    ? feature.trim().split(/\s+/).filter(w => w).length
    : 0

  return (
    <div className="relative">
      <div className="flex items-start gap-2">
        <div className="flex-1">
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Feature {index + 1}
          </label>
          <textarea
            value={feature}
            onChange={(e) => onUpdate(e.target.value)}
            maxLength={maxLength}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-y min-h-[80px]"
            placeholder="Describe this feature (1-2 words for simple features, or write detailed requirements)..."
          />
          <div className="mt-1 flex items-center justify-between text-xs text-gray-500">
            <span>{feature.length} / {maxLength} characters</span>
            <span>{wordCount} word{wordCount !== 1 ? 's' : ''}</span>
          </div>
        </div>
        <button
          type="button"
          onClick={onRemove}
          disabled={!canRemove}
          className="mt-7 p-2 text-gray-400 hover:text-red-500 disabled:opacity-50 disabled:cursor-not-allowed"
          title={!canRemove ? "Cannot remove the last feature" : "Remove feature"}
          aria-label={!canRemove ? "Cannot remove the last feature" : `Remove feature ${index + 1}`}
        >
          <X className="w-5 h-5" aria-hidden="true" />
        </button>
      </div>
    </div>
  )
}
