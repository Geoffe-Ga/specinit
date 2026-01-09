import type { TechStack } from '../../types'
import { TechStackSelector } from '../TechStackSelector'

interface StepTechStackProps {
  value: TechStack
  onChange: (techStack: TechStack) => void
  platforms: string[]
}

export function StepTechStack({ value, onChange, platforms }: StepTechStackProps) {
  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h2 className="text-xl font-semibold mb-4">Tech Stack</h2>
      <p className="text-gray-600 mb-4">
        Select the technologies for your project.
      </p>

      <TechStackSelector
        value={value}
        onChange={onChange}
        platforms={platforms}
      />
    </div>
  )
}
