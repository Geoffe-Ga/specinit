import { FeatureList } from '../FeatureList'

interface StepFeaturesProps {
  features: string[]
  onChange: (features: string[]) => void
  error?: string
}

export function StepFeatures({ features, onChange, error }: StepFeaturesProps) {
  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h2 className="text-xl font-semibold mb-4">Features</h2>
      <p className="text-gray-600 mb-4">
        Add up to 20 features for your project.
      </p>

      <FeatureList
        features={features}
        onChange={onChange}
        error={error}
      />
    </div>
  )
}
