import { useState } from 'react'
import { ExternalLink, Check, AlertCircle, Key } from 'lucide-react'
import type { GitHubConfig } from '../types'

interface GitHubSetupProps {
  value: GitHubConfig
  onChange: (config: GitHubConfig) => void
  projectName: string
}

export function GitHubSetup({ value, onChange, projectName }: GitHubSetupProps) {
  const [showTokenSetup, setShowTokenSetup] = useState(false)
  const [token, setToken] = useState('')
  const [validating, setValidating] = useState(false)
  const [validationError, setValidationError] = useState('')

  const handleModeChange = (enabled: boolean) => {
    onChange({ ...value, enabled })
  }

  const handleValidateToken = async () => {
    if (!token.startsWith('ghp_') && !token.startsWith('github_pat_')) {
      setValidationError('Invalid token format. Token should start with "ghp_" or "github_pat_"')
      return
    }

    setValidating(true)
    setValidationError('')

    try {
      const response = await fetch('/api/github/validate-token', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ token }),
      })

      if (response.ok) {
        onChange({ ...value, tokenConfigured: true })
        setShowTokenSetup(false)
        setToken('')
      } else {
        const data = await response.json()
        setValidationError(data.message || 'Token validation failed')
      }
    } catch {
      setValidationError('Failed to validate token. Please try again.')
    } finally {
      setValidating(false)
    }
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-4">
        <label className="flex items-center gap-2 cursor-pointer">
          <input
            type="radio"
            name="github-mode"
            checked={!value.enabled}
            onChange={() => handleModeChange(false)}
            className="w-4 h-4 text-blue-600"
          />
          <span className="font-medium">Local Mode</span>
        </label>
        <span className="text-sm text-gray-500">Generate files without GitHub</span>
      </div>

      <div className="flex items-center gap-4">
        <label className="flex items-center gap-2 cursor-pointer">
          <input
            type="radio"
            name="github-mode"
            checked={value.enabled}
            onChange={() => handleModeChange(true)}
            className="w-4 h-4 text-blue-600"
          />
          <span className="font-medium">GitHub Mode</span>
        </label>
        <span className="text-sm text-gray-500">Issue-driven development with PRs</span>
      </div>

      {value.enabled && (
        <div className="mt-4 p-4 bg-gray-50 rounded-lg space-y-4">
          {/* Repository URL */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Repository URL
            </label>
            <input
              type="text"
              value={value.repoUrl}
              onChange={(e) => onChange({ ...value, repoUrl: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder={`https://github.com/username/${projectName || 'my-project'}`}
            />
          </div>

          {/* Create repo option */}
          <label className="flex items-center gap-2 cursor-pointer">
            <input
              type="checkbox"
              checked={value.createRepo}
              onChange={(e) => onChange({ ...value, createRepo: e.target.checked })}
              className="w-4 h-4 text-blue-600 rounded"
            />
            <span className="text-sm">Create repository if it doesn't exist</span>
          </label>

          {/* Token configuration */}
          <div className="flex items-center gap-2">
            <span className="text-sm font-medium">GitHub Token:</span>
            {value.tokenConfigured ? (
              <span className="flex items-center gap-1 text-sm text-green-600">
                <Check className="w-4 h-4" />
                Configured
              </span>
            ) : (
              <button
                type="button"
                onClick={() => setShowTokenSetup(true)}
                className="text-sm text-blue-600 hover:text-blue-800"
              >
                Configure Token...
              </button>
            )}
          </div>

          {/* Token setup modal/panel */}
          {showTokenSetup && (
            <div className="p-4 bg-white border border-gray-200 rounded-lg space-y-3">
              <h4 className="font-medium flex items-center gap-2">
                <Key className="w-4 h-4" />
                GitHub Token Setup
              </h4>

              <ol className="text-sm text-gray-600 space-y-2 ml-4 list-decimal">
                <li>
                  Go to{' '}
                  <a
                    href="https://github.com/settings/tokens/new"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-blue-600 hover:underline inline-flex items-center gap-1"
                  >
                    GitHub Token Settings
                    <ExternalLink className="w-3 h-3" />
                  </a>
                </li>
                <li>Note: "SpecInit CLI Access"</li>
                <li>
                  Select scopes:
                  <ul className="ml-4 list-disc text-gray-500">
                    <li><strong>repo</strong> - Full control of repositories</li>
                    <li><strong>workflow</strong> - Update GitHub Actions</li>
                  </ul>
                </li>
                <li>Generate and paste token below:</li>
              </ol>

              <input
                type="password"
                value={token}
                onChange={(e) => setToken(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
                placeholder="ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
              />

              {validationError && (
                <p className="text-sm text-red-600 flex items-center gap-1">
                  <AlertCircle className="w-4 h-4" />
                  {validationError}
                </p>
              )}

              <div className="flex gap-2">
                <button
                  type="button"
                  onClick={handleValidateToken}
                  disabled={!token || validating}
                  className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
                >
                  {validating ? 'Validating...' : 'Validate & Save'}
                </button>
                <button
                  type="button"
                  onClick={() => {
                    setShowTokenSetup(false)
                    setToken('')
                    setValidationError('')
                  }}
                  className="px-4 py-2 text-gray-600 hover:text-gray-800"
                >
                  Cancel
                </button>
              </div>
            </div>
          )}

          {/* YOLO Mode */}
          <div className="pt-3 border-t border-gray-200">
            <label className="flex items-start gap-2 cursor-pointer">
              <input
                type="checkbox"
                checked={value.yoloMode}
                onChange={(e) => onChange({ ...value, yoloMode: e.target.checked })}
                className="w-4 h-4 text-blue-600 rounded mt-0.5"
              />
              <div>
                <span className="font-medium">Enable YOLO Mode</span>
                <p className="text-sm text-gray-500">
                  Auto-resolve CI failures and review feedback (recursively iterate until all checks pass)
                </p>
              </div>
            </label>
          </div>

          {/* Cost warning */}
          <p className="text-xs text-gray-500 pt-2">
            GitHub Mode may increase API costs by $0.50-3.00 depending on complexity and YOLO mode usage.
          </p>
        </div>
      )}
    </div>
  )
}
