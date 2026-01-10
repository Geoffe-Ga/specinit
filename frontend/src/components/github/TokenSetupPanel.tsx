import { AlertCircle, ExternalLink, Key } from 'lucide-react'
import { useState } from 'react'

interface TokenSetupPanelProps {
  onTokenConfigured: () => void
  onCancel: () => void
}

export function TokenSetupPanel({ onTokenConfigured, onCancel }: TokenSetupPanelProps) {
  const [token, setToken] = useState('')
  const [validating, setValidating] = useState(false)
  const [validationError, setValidationError] = useState('')

  const handleValidateToken = async () => {
    const formatError = validateTokenFormat(token)
    if (formatError) {
      setValidationError(formatError)
      return
    }

    setValidating(true)
    setValidationError('')

    const result = await validateTokenWithServer(token)
    setValidating(false)

    if (result.success) {
      onTokenConfigured()
      setToken('')
    } else {
      setValidationError(result.error)
    }
  }

  const handleCancel = () => {
    setToken('')
    setValidationError('')
    onCancel()
  }

  return (
    <div className="p-4 bg-white border border-gray-200 rounded-lg space-y-3">
      <h4 className="font-medium flex items-center gap-2">
        <Key className="w-4 h-4" />
        GitHub Token Setup
      </h4>

      <TokenInstructions />

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

      <TokenSetupButtons
        token={token}
        validating={validating}
        onValidate={handleValidateToken}
        onCancel={handleCancel}
      />
    </div>
  )
}

function TokenInstructions() {
  return (
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
      <li>Note: &quot;SpecInit CLI Access&quot;</li>
      <li>
        Select scopes:
        <ul className="ml-4 list-disc text-gray-500">
          <li><strong>repo</strong> - Full control of repositories</li>
          <li><strong>workflow</strong> - Update GitHub Actions</li>
        </ul>
      </li>
      <li>Generate and paste token below:</li>
    </ol>
  )
}

interface TokenSetupButtonsProps {
  token: string
  validating: boolean
  onValidate: () => void
  onCancel: () => void
}

function TokenSetupButtons({ token, validating, onValidate, onCancel }: TokenSetupButtonsProps) {
  return (
    <div className="flex gap-2">
      <button
        type="button"
        onClick={onValidate}
        disabled={!token || validating}
        className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
      >
        {validating ? 'Validating...' : 'Validate & Save'}
      </button>
      <button
        type="button"
        onClick={onCancel}
        className="px-4 py-2 text-gray-600 hover:text-gray-800"
      >
        Cancel
      </button>
    </div>
  )
}

function validateTokenFormat(token: string): string | null {
  if (!token.startsWith('ghp_') && !token.startsWith('github_pat_')) {
    return 'Invalid token format. Token should start with "ghp_" or "github_pat_"'
  }
  return null
}

async function validateTokenWithServer(token: string): Promise<{ success: boolean; error: string }> {
  try {
    const response = await fetch('/api/github/validate-token', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ token }),
    })

    if (response.ok) {
      return { success: true, error: '' }
    }

    const data = await response.json()
    return { success: false, error: data.message || 'Token validation failed' }
  } catch {
    return { success: false, error: 'Failed to validate token. Please try again.' }
  }
}
