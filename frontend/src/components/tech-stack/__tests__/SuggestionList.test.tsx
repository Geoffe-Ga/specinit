import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, it, expect, vi } from 'vitest'

import type { TechStack } from '../../../types'
import { SuggestionList } from '../SuggestionList'

const mockTechStack: TechStack = { frontend: [], backend: [], database: [], tools: [] }

describe('SuggestionList', () => {
  it('should render suggestions', () => {
    const mockAdd = vi.fn()
    const mockGetMore = vi.fn()
    const mockSkip = vi.fn()
    render(
      <SuggestionList
        suggestions={['React', 'Vue']}
        value={mockTechStack}
        isLoading={false}
        onAdd={mockAdd}
        onGetMore={mockGetMore}
        onSkip={mockSkip}
      />
    )
    expect(screen.getByText('React')).toBeInTheDocument()
    expect(screen.getByText('Vue')).toBeInTheDocument()
  })

  it('should call onGetMore when get more button clicked', async () => {
    const mockAdd = vi.fn()
    const mockGetMore = vi.fn()
    const mockSkip = vi.fn()
    const user = userEvent.setup()
    render(
      <SuggestionList
        suggestions={['React']}
        value={mockTechStack}
        isLoading={false}
        onAdd={mockAdd}
        onGetMore={mockGetMore}
        onSkip={mockSkip}
      />
    )
    const getMoreButton = screen.getByRole('button', { name: /get more tech stack suggestions/i })
    await user.click(getMoreButton)
    expect(mockGetMore).toHaveBeenCalled()
  })

  it('should call onSkip when skip all button clicked', async () => {
    const mockAdd = vi.fn()
    const mockGetMore = vi.fn()
    const mockSkip = vi.fn()
    const user = userEvent.setup()
    render(
      <SuggestionList
        suggestions={['React']}
        value={mockTechStack}
        isLoading={false}
        onAdd={mockAdd}
        onGetMore={mockGetMore}
        onSkip={mockSkip}
      />
    )
    const skipButton = screen.getByRole('button', { name: /skip suggestions and choose manually/i })
    await user.click(skipButton)
    expect(mockSkip).toHaveBeenCalled()
  })
})
