import { AestheticsSelector } from '../AestheticsSelector'

interface StepAestheticsProps {
  selected: string[]
  onChange: (aesthetics: string[]) => void
  error?: string
}

export function StepAesthetics({ selected, onChange, error }: StepAestheticsProps) {
  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h2 className="text-xl font-semibold mb-4">UX Aesthetics</h2>
      <p className="text-gray-600 mb-4">
        Select up to 3 aesthetic principles for your project.
      </p>

      <AestheticsSelector
        selected={selected}
        onChange={onChange}
        error={error}
      />
    </div>
  )
}
