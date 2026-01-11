import { render, screen } from '@testing-library/react'
import { describe, it, expect, vi } from 'vitest'

import type { TechStack } from '../../../types'
import { SuggestionsPanel } from '../SuggestionsPanel'

const mockTechStack: TechStack = { frontend: [], backend: [], database: [], tools: [] }

interface RenderOptions {
  enabled: boolean
  shown: boolean
  loading: boolean
  error: string | null
  suggestions: string[]
}

function renderPanel(options: RenderOptions) {
  return render(
    <SuggestionsPanel
      suggestionsEnabled={options.enabled}
      showSuggestions={options.shown}
      isLoading={options.loading}
      error={options.error}
      suggestions={options.suggestions}
      value={mockTechStack}
      onGetSuggestions={vi.fn()}
      onAddSuggestion={vi.fn()}
      onSkipAll={vi.fn()}
    />
  )
}

describe('SuggestionsPanel', () => {
  it('should render nothing when suggestions disabled', () => {
    const { container } = renderPanel({ enabled: false, shown: false, loading: false, error: null, suggestions: [] })
    expect(container.firstChild).toBeNull()
  })

  it('should render loading state when loading', () => {
    renderPanel({ enabled: true, shown: true, loading: true, error: null, suggestions: [] })
    expect(screen.getByText(/generating tech stack recommendations/i)).toBeInTheDocument()
  })

  it('should render error state when error exists', () => {
    renderPanel({ enabled: true, shown: true, loading: false, error: 'Test error', suggestions: [] })
    expect(screen.getByText('Test error')).toBeInTheDocument()
  })

  it('should render empty state when no suggestions', () => {
    renderPanel({ enabled: true, shown: true, loading: false, error: null, suggestions: [] })
    expect(screen.getByText(/no suggestions available/i)).toBeInTheDocument()
  })

  it('should render suggestions when available', () => {
    renderPanel({ enabled: true, shown: true, loading: false, error: null, suggestions: ['React', 'Vue'] })
    expect(screen.getByText('React')).toBeInTheDocument()
    expect(screen.getByText('Vue')).toBeInTheDocument()
    expect(screen.getByText(/or choose manually/i)).toBeInTheDocument()
  })
})
