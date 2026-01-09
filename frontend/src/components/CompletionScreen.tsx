import { CheckCircle, Folder, DollarSign, Clock } from 'lucide-react'

import type { GenerationResult } from '../types'

interface CompletionScreenProps {
  result: GenerationResult
  onNewProject: () => void
}

export function CompletionScreen({ result, onNewProject }: CompletionScreenProps) {
  const formatTime = (seconds: number) => {
    if (seconds < 60) {
      return `${Math.round(seconds)}s`
    }
    const minutes = Math.floor(seconds / 60)
    const remainingSeconds = Math.round(seconds % 60)
    return `${minutes}m ${remainingSeconds}s`
  }

  return (
    <div className="bg-white rounded-lg shadow p-8 text-center">
      <CheckCircle className="w-16 h-16 text-green-500 mx-auto mb-4" />

      <h2 className="text-2xl font-bold text-gray-900 mb-2">Project Complete!</h2>
      <p className="text-gray-600 mb-8">Your project has been successfully generated.</p>

      <div className="grid grid-cols-3 gap-4 mb-8">
        <div className="bg-gray-50 rounded-lg p-4">
          <Folder className="w-6 h-6 text-gray-400 mx-auto mb-2" />
          <div className="text-sm text-gray-500">Location</div>
          <div className="text-sm font-mono truncate" title={result.path}>
            {result.path}
          </div>
        </div>

        <div className="bg-gray-50 rounded-lg p-4">
          <DollarSign className="w-6 h-6 text-gray-400 mx-auto mb-2" />
          <div className="text-sm text-gray-500">Total Cost</div>
          <div className="text-lg font-semibold">${result.totalCost.toFixed(2)}</div>
        </div>

        <div className="bg-gray-50 rounded-lg p-4">
          <Clock className="w-6 h-6 text-gray-400 mx-auto mb-2" />
          <div className="text-sm text-gray-500">Generation Time</div>
          <div className="text-lg font-semibold">{formatTime(result.generationTime)}</div>
        </div>
      </div>

      <div className="bg-gray-900 rounded-lg p-4 text-left mb-8">
        <p className="text-gray-400 text-sm mb-2">Next steps:</p>
        <code className="text-green-400 text-sm">
          cd {result.path.split('/').pop()}
          <br />
          npm install  # or pip install -e .
          <br />
          npm run dev  # or python -m your_app
        </code>
      </div>

      <button
        onClick={onNewProject}
        className="px-6 py-3 bg-blue-600 text-white rounded-md hover:bg-blue-700"
      >
        Create Another Project
      </button>
    </div>
  )
}
