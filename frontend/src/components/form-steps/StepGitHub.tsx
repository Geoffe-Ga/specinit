import type { GitHubConfig } from '../../types'
import { GitHubSetup } from '../GitHubSetup'

interface StepGitHubProps {
  value: GitHubConfig
  onChange: (github: GitHubConfig) => void
  projectName: string
}

export function StepGitHub({ value, onChange, projectName }: StepGitHubProps) {
  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h2 className="text-xl font-semibold mb-4">GitHub Integration</h2>
      <p className="text-gray-600 mb-4">
        Choose how you want SpecInit to generate your project. GitHub Mode creates
        issues, branches, and PRs for better tracking and accuracy.
      </p>

      <GitHubSetup
        value={value}
        onChange={onChange}
        projectName={projectName}
      />
    </div>
  )
}
