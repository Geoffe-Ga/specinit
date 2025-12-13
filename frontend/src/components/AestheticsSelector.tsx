import { AESTHETICS } from '../types'

interface AestheticsSelectorProps {
  selected: string[]
  onChange: (aesthetics: string[]) => void
  error?: string
}

export function AestheticsSelector({ selected, onChange, error }: AestheticsSelectorProps) {
  const toggleAesthetic = (aestheticId: string) => {
    if (selected.includes(aestheticId)) {
      onChange(selected.filter((a) => a !== aestheticId))
    } else if (selected.length < 3) {
      onChange([...selected, aestheticId])
    }
  }

  return (
    <div>
      <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
        {AESTHETICS.map((aesthetic) => (
          <button
            key={aesthetic.id}
            type="button"
            onClick={() => toggleAesthetic(aesthetic.id)}
            disabled={!selected.includes(aesthetic.id) && selected.length >= 3}
            className={`p-4 rounded-lg border-2 text-center transition-colors ${
              selected.includes(aesthetic.id)
                ? 'border-blue-500 bg-blue-50'
                : 'border-gray-200 hover:border-gray-300'
            } disabled:opacity-50 disabled:cursor-not-allowed`}
          >
            <span className="font-medium">{aesthetic.label}</span>
          </button>
        ))}
      </div>
      {error && <p className="mt-2 text-sm text-red-600">{error}</p>}
      <p className="mt-2 text-sm text-gray-500">{selected.length}/3 selected</p>
    </div>
  )
}
