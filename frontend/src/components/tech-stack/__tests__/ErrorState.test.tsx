import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, it, expect, vi } from 'vitest'

import { ErrorState } from '../ErrorState'

describe('ErrorState', () => {
  it('should render error message', () => {
    const mockRetry = vi.fn()
    const mockDismiss = vi.fn()
    render(<ErrorState error="Test error" isLoading={false} onRetry={mockRetry} onDismiss={mockDismiss} />)
    expect(screen.getByText('Test error')).toBeInTheDocument()
  })

  it('should call onRetry when retry button clicked', async () => {
    const mockRetry = vi.fn()
    const mockDismiss = vi.fn()
    const user = userEvent.setup()
    render(<ErrorState error="Test error" isLoading={false} onRetry={mockRetry} onDismiss={mockDismiss} />)
    const retryButton = screen.getByRole('button', { name: /retry loading tech stack suggestions/i })
    await user.click(retryButton)
    expect(mockRetry).toHaveBeenCalled()
  })

  it('should call onDismiss when dismiss button clicked', async () => {
    const mockRetry = vi.fn()
    const mockDismiss = vi.fn()
    const user = userEvent.setup()
    render(<ErrorState error="Test error" isLoading={false} onRetry={mockRetry} onDismiss={mockDismiss} />)
    const dismissButton = screen.getByRole('button', { name: /dismiss error and choose manually/i })
    await user.click(dismissButton)
    expect(mockDismiss).toHaveBeenCalled()
  })
})
