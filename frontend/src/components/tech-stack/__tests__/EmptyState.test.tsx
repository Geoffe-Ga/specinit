import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, it, expect, vi } from 'vitest'

import { EmptyState } from '../EmptyState'

describe('EmptyState', () => {
  it('should render empty state message', () => {
    const mockSkip = vi.fn()
    render(<EmptyState onSkipAll={mockSkip} />)
    expect(screen.getByText(/no suggestions available/i)).toBeInTheDocument()
  })

  it('should call onSkipAll when continue button clicked', async () => {
    const mockSkip = vi.fn()
    const user = userEvent.setup()
    render(<EmptyState onSkipAll={mockSkip} />)
    const continueButton = screen.getByRole('button', { name: /skip suggestions and continue choosing technologies manually/i })
    await user.click(continueButton)
    expect(mockSkip).toHaveBeenCalled()
  })
})
