import { Check, Loader2, Circle } from 'lucide-react'
import { useEffect, useState, useRef } from 'react'

import type { ProjectConfig, GenerationResult, StepProgress } from '../types'

interface GenerationProgressProps {
  config: ProjectConfig
  onComplete: (result: GenerationResult) => void
}

const STEPS = [
  { id: 'product_spec', name: 'Product specification' },
  { id: 'structure', name: 'Project structure' },
  { id: 'documentation', name: 'Documentation' },
  { id: 'tooling', name: 'Developer tooling' },
  { id: 'validation', name: 'Validation' },
  { id: 'dependencies', name: 'Dependencies' },
  { id: 'git_init', name: 'Git initialization' },
  { id: 'demo_code', name: 'Demo code' },
]

function useGenerationWebSocket(
  config: ProjectConfig,
  onComplete: (result: GenerationResult) => void
) {
  const [steps, setSteps] = useState<Record<string, StepProgress>>(() =>
    Object.fromEntries(STEPS.map((s) => [s.id, { step: s.id, status: 'pending' as const }]))
  )
  const [totalCost, setTotalCost] = useState(0)
  const [error, setError] = useState<string | null>(null)
  const wsRef = useRef<WebSocket | null>(null)

  useEffect(() => {
    const ws = new WebSocket(`ws://localhost:8765/ws/generate`)
    wsRef.current = ws

    ws.onopen = () => {
      ws.send(
        JSON.stringify({
          name: config.name,
          platforms: config.platforms,
          user_story: config.userStory,
          features: config.features,
          tech_stack: config.techStack,
          aesthetics: config.aesthetics,
        })
      )
    }

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data)

      if (data.type === 'progress') {
        setSteps((prev) => ({
          ...prev,
          [data.step]: { step: data.step, status: data.status, details: data.details },
        }))

        if (data.details?.cost) {
          setTotalCost((prev) => prev + data.details.cost)
        }
      } else if (data.type === 'complete') {
        onComplete({
          path: data.result.path,
          totalCost: data.result.total_cost,
          generationTime: data.result.generation_time,
        })
      } else if (data.type === 'error') {
        setError(data.message)
      }
    }

    ws.onerror = () => {
      setError('Connection error. Please try again.')
    }

    return () => {
      ws.close()
    }
  }, [config, onComplete])

  return { steps, totalCost, error }
}

function ErrorDisplay({ message }: { message: string }) {
  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="text-center">
        <div className="text-red-500 text-xl mb-4">Generation Error</div>
        <p className="text-gray-600">{message}</p>
      </div>
    </div>
  )
}

function getStepIcon(status: StepProgress['status']) {
  switch (status) {
    case 'completed':
      return <Check className="w-5 h-5 text-green-500" />
    case 'in_progress':
      return <Loader2 className="w-5 h-5 text-blue-500 animate-spin" />
    default:
      return <Circle className="w-5 h-5 text-gray-300" />
  }
}

function StepItem({ step, progress }: { step: { id: string; name: string }; progress?: StepProgress }) {
  const status = progress?.status || 'pending'
  const isInProgress = status === 'in_progress'
  const isCompleted = status === 'completed'

  return (
    <div className={`flex items-center gap-4 p-3 rounded-lg ${isInProgress ? 'bg-blue-50' : ''}`}>
      {getStepIcon(status)}
      <span
        className={`flex-1 ${
          isCompleted ? 'text-gray-500' : isInProgress ? 'text-blue-700 font-medium' : 'text-gray-400'
        }`}
      >
        {step.name}
      </span>
      {progress?.details?.cost && (
        <span className="text-sm text-gray-500">${progress.details.cost.toFixed(2)}</span>
      )}
    </div>
  )
}

export function GenerationProgress({ config, onComplete }: GenerationProgressProps) {
  const { steps, totalCost, error } = useGenerationWebSocket(config, onComplete)

  if (error) {
    return <ErrorDisplay message={error} />
  }

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h2 className="text-xl font-semibold mb-2">Generating: {config.name}</h2>
      <p className="text-gray-600 mb-6">Please wait while we create your project...</p>

      <div className="space-y-4">
        {STEPS.map((step) => (
          <StepItem key={step.id} step={step} progress={steps[step.id]} />
        ))}
      </div>

      <div className="mt-6 pt-4 border-t border-gray-200">
        <div className="flex justify-between text-sm text-gray-600">
          <span>API cost so far:</span>
          <span className="font-medium">${totalCost.toFixed(2)}</span>
        </div>
      </div>
    </div>
  )
}
