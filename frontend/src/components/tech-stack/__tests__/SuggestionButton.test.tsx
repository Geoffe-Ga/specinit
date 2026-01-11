import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, it, expect, vi } from 'vitest'

import { SuggestionButton } from '../SuggestionButton'

describe('SuggestionButton', () => {
  it('should render suggestion text', () => {
    const mockAdd = vi.fn()
    render(<SuggestionButton suggestion="React" isAdded={false} onAdd={mockAdd} />)
    expect(screen.getByText('React')).toBeInTheDocument()
  })

  it('should call onAdd when clicked', async () => {
    const mockAdd = vi.fn()
    const user = userEvent.setup()
    render(<SuggestionButton suggestion="React" isAdded={false} onAdd={mockAdd} />)
    await user.click(screen.getByRole('button'))
    expect(mockAdd).toHaveBeenCalledWith('React')
  })

  it('should show checkmark when added', () => {
    const mockAdd = vi.fn()
    render(<SuggestionButton suggestion="React" isAdded={true} onAdd={mockAdd} />)
    expect(screen.getByText('✓')).toBeInTheDocument()
  })

  it('should be disabled when added', () => {
    const mockAdd = vi.fn()
    render(<SuggestionButton suggestion="React" isAdded={true} onAdd={mockAdd} />)
    expect(screen.getByRole('button')).toBeDisabled()
  })
})
