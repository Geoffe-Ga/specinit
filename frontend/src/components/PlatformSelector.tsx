import { PLATFORMS } from '../types'

interface PlatformSelectorProps {
  selected: string[]
  onChange: (platforms: string[]) => void
  error?: string
}

export function PlatformSelector({ selected, onChange, error }: PlatformSelectorProps) {
  const togglePlatform = (platformId: string) => {
    if (selected.includes(platformId)) {
      onChange(selected.filter((p) => p !== platformId))
    } else {
      onChange([...selected, platformId])
    }
  }

  return (
    <div>
      <label className="block text-sm font-medium text-gray-700 mb-2">
        Target Platforms
      </label>
      <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
        {PLATFORMS.map((platform) => (
          <button
            key={platform.id}
            type="button"
            onClick={() => togglePlatform(platform.id)}
            className={`p-4 rounded-lg border-2 text-left transition-colors ${
              selected.includes(platform.id)
                ? 'border-blue-500 bg-blue-50'
                : 'border-gray-200 hover:border-gray-300'
            }`}
          >
            <span className="text-2xl mb-2 block">{platform.icon}</span>
            <span className="font-medium">{platform.label}</span>
          </button>
        ))}
      </div>
      {error && <p className="mt-2 text-sm text-red-600">{error}</p>}
    </div>
  )
}
