import { Check } from 'lucide-react'
import { useState } from 'react'

import type { GitHubConfig } from '../types'

import { ModeSelector, RepositoryConfig, TokenSetupPanel, YoloModeToggle } from './github'

interface GitHubSetupProps {
  value: GitHubConfig
  onChange: (config: GitHubConfig) => void
  projectName: string
}

export function GitHubSetup({ value, onChange, projectName }: GitHubSetupProps) {
  const [showTokenSetup, setShowTokenSetup] = useState(false)

  const handleModeChange = (enabled: boolean) => {
    onChange({ ...value, enabled })
  }

  const handleTokenConfigured = () => {
    onChange({ ...value, tokenConfigured: true })
    setShowTokenSetup(false)
  }

  return (
    <div className="space-y-4">
      <ModeSelector enabled={value.enabled} onModeChange={handleModeChange} />

      {value.enabled && (
        <GitHubModePanel
          value={value}
          onChange={onChange}
          projectName={projectName}
          showTokenSetup={showTokenSetup}
          onShowTokenSetup={() => setShowTokenSetup(true)}
          onTokenConfigured={handleTokenConfigured}
          onCancelTokenSetup={() => setShowTokenSetup(false)}
        />
      )}
    </div>
  )
}

interface GitHubModePanelProps {
  value: GitHubConfig
  onChange: (config: GitHubConfig) => void
  projectName: string
  showTokenSetup: boolean
  onShowTokenSetup: () => void
  onTokenConfigured: () => void
  onCancelTokenSetup: () => void
}

function GitHubModePanel({
  value,
  onChange,
  projectName,
  showTokenSetup,
  onShowTokenSetup,
  onTokenConfigured,
  onCancelTokenSetup,
}: GitHubModePanelProps) {
  return (
    <div className="mt-4 p-4 bg-gray-50 rounded-lg space-y-4">
      <RepositoryConfig
        repoUrl={value.repoUrl}
        createRepo={value.createRepo}
        projectName={projectName}
        onRepoUrlChange={(repoUrl) => onChange({ ...value, repoUrl })}
        onCreateRepoChange={(createRepo) => onChange({ ...value, createRepo })}
      />

      <TokenStatus
        tokenConfigured={value.tokenConfigured}
        onConfigureClick={onShowTokenSetup}
      />

      {showTokenSetup && (
        <TokenSetupPanel
          onTokenConfigured={onTokenConfigured}
          onCancel={onCancelTokenSetup}
        />
      )}

      <YoloModeToggle
        enabled={value.yoloMode}
        onChange={(yoloMode) => onChange({ ...value, yoloMode })}
      />

      <p className="text-xs text-gray-500 pt-2">
        GitHub Mode may increase API costs by $0.50-3.00 depending on complexity and YOLO mode usage.
      </p>
    </div>
  )
}

interface TokenStatusProps {
  tokenConfigured: boolean
  onConfigureClick: () => void
}

function TokenStatus({ tokenConfigured, onConfigureClick }: TokenStatusProps) {
  return (
    <div className="flex items-center gap-2">
      <span className="text-sm font-medium">GitHub Token:</span>
      {tokenConfigured ? (
        <span className="flex items-center gap-1 text-sm text-green-600">
          <Check className="w-4 h-4" />
          Configured
        </span>
      ) : (
        <button
          type="button"
          onClick={onConfigureClick}
          className="text-sm text-blue-600 hover:text-blue-800"
        >
          Configure Token...
        </button>
      )}
    </div>
  )
}
