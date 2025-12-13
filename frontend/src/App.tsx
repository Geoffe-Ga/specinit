import { useState } from 'react'
import { ProjectForm } from './components/ProjectForm'
import { GenerationProgress } from './components/GenerationProgress'
import { CompletionScreen } from './components/CompletionScreen'
import type { ProjectConfig, GenerationResult } from './types'

type AppState = 'form' | 'generating' | 'complete'

function App() {
  const [state, setState] = useState<AppState>('form')
  const [projectConfig, setProjectConfig] = useState<ProjectConfig | null>(null)
  const [result, setResult] = useState<GenerationResult | null>(null)

  const handleFormSubmit = (config: ProjectConfig) => {
    setProjectConfig(config)
    setState('generating')
  }

  const handleGenerationComplete = (generationResult: GenerationResult) => {
    setResult(generationResult)
    setState('complete')
  }

  const handleReset = () => {
    setProjectConfig(null)
    setResult(null)
    setState('form')
  }

  return (
    <div className="min-h-screen">
      <header className="bg-white shadow-sm">
        <div className="max-w-4xl mx-auto px-4 py-4">
          <h1 className="text-2xl font-bold text-gray-900">SpecInit</h1>
          <p className="text-sm text-gray-600">AI-Powered Project Generator</p>
        </div>
      </header>

      <main className="max-w-4xl mx-auto px-4 py-8">
        {state === 'form' && (
          <ProjectForm onSubmit={handleFormSubmit} />
        )}

        {state === 'generating' && projectConfig && (
          <GenerationProgress
            config={projectConfig}
            onComplete={handleGenerationComplete}
          />
        )}

        {state === 'complete' && result && (
          <CompletionScreen
            result={result}
            onNewProject={handleReset}
          />
        )}
      </main>
    </div>
  )
}

export default App
