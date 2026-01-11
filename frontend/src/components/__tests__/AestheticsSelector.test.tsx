import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, it, expect, vi, beforeEach } from 'vitest'

import { AestheticsSelector } from '../AestheticsSelector'

const mockOnChange = vi.fn()

describe('AestheticsSelector - Rendering', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('should render all aesthetic options', () => {
    render(<AestheticsSelector selected={[]} onChange={mockOnChange} />)

    expect(screen.getByText('Minimalist')).toBeInTheDocument()
    expect(screen.getByText('Professional')).toBeInTheDocument()
    expect(screen.getByText('Playful')).toBeInTheDocument()
    expect(screen.getByText('Accessible-First')).toBeInTheDocument()
    expect(screen.getByText('Modern')).toBeInTheDocument()
    expect(screen.getByText('Retro')).toBeInTheDocument()
  })

  it('should display selection counter', () => {
    render(<AestheticsSelector selected={['minimalist', 'modern']} onChange={mockOnChange} />)

    expect(screen.getByText('2/3 selected')).toBeInTheDocument()
  })

  it('should show 0/3 when nothing is selected', () => {
    render(<AestheticsSelector selected={[]} onChange={mockOnChange} />)

    expect(screen.getByText('0/3 selected')).toBeInTheDocument()
  })
})

describe('AestheticsSelector - Selection State', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('should show selected aesthetics with different styling', () => {
    render(<AestheticsSelector selected={['minimalist', 'professional']} onChange={mockOnChange} />)

    const minimalistButton = screen.getByText('Minimalist').closest('button')
    const professionalButton = screen.getByText('Professional').closest('button')
    const playfulButton = screen.getByText('Playful').closest('button')

    // Selected items should have blue border and background
    expect(minimalistButton).toHaveClass('border-blue-500', 'bg-blue-50')
    expect(professionalButton).toHaveClass('border-blue-500', 'bg-blue-50')
    // Unselected should have gray border
    expect(playfulButton).toHaveClass('border-gray-200')
  })

  it('should disable unselected aesthetics when 3 are selected', () => {
    render(
      <AestheticsSelector
        selected={['minimalist', 'professional', 'playful']}
        onChange={mockOnChange}
      />
    )

    const minimalistButton = screen.getByText('Minimalist').closest('button')
    const modernButton = screen.getByText('Modern').closest('button')

    // Selected items should be enabled
    expect(minimalistButton).not.toBeDisabled()
    // Unselected items should be disabled
    expect(modernButton).toBeDisabled()
  })

  it('should not disable unselected aesthetics when less than 3 are selected', () => {
    render(<AestheticsSelector selected={['minimalist']} onChange={mockOnChange} />)

    const modernButton = screen.getByText('Modern').closest('button')

    expect(modernButton).not.toBeDisabled()
  })
})

describe('AestheticsSelector - Toggle Behavior', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('should add aesthetic when clicking unselected', async () => {
    const user = userEvent.setup()
    render(<AestheticsSelector selected={[]} onChange={mockOnChange} />)

    const minimalistButton = screen.getByText('Minimalist').closest('button')!
    await user.click(minimalistButton)

    expect(mockOnChange).toHaveBeenCalledWith(['minimalist'])
  })

  it('should remove aesthetic when clicking selected', async () => {
    const user = userEvent.setup()
    render(<AestheticsSelector selected={['minimalist', 'modern']} onChange={mockOnChange} />)

    const minimalistButton = screen.getByText('Minimalist').closest('button')!
    await user.click(minimalistButton)

    expect(mockOnChange).toHaveBeenCalledWith(['modern'])
  })

  it('should preserve other selections when adding', async () => {
    const user = userEvent.setup()
    render(<AestheticsSelector selected={['minimalist']} onChange={mockOnChange} />)

    const modernButton = screen.getByText('Modern').closest('button')!
    await user.click(modernButton)

    expect(mockOnChange).toHaveBeenCalledWith(['minimalist', 'modern'])
  })

  it('should preserve other selections when removing', async () => {
    const user = userEvent.setup()
    render(
      <AestheticsSelector
        selected={['minimalist', 'professional', 'playful']}
        onChange={mockOnChange}
      />
    )

    const professionalButton = screen.getByText('Professional').closest('button')!
    await user.click(professionalButton)

    expect(mockOnChange).toHaveBeenCalledWith(['minimalist', 'playful'])
  })
})

describe('AestheticsSelector - Maximum Selection Limit', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('should not allow adding more than 3 aesthetics', async () => {
    const user = userEvent.setup()
    render(
      <AestheticsSelector
        selected={['minimalist', 'professional', 'playful']}
        onChange={mockOnChange}
      />
    )

    const modernButton = screen.getByText('Modern').closest('button')!
    await user.click(modernButton)

    // onChange should not be called since limit is reached
    expect(mockOnChange).not.toHaveBeenCalled()
  })

  it('should allow selecting up to 3 aesthetics', async () => {
    const user = userEvent.setup()
    const { rerender } = render(<AestheticsSelector selected={[]} onChange={mockOnChange} />)

    // Select 3 aesthetics sequentially
    const aesthetics = ['minimalist', 'professional', 'playful']
    let selected: string[] = []

    for (const aesthetic of aesthetics) {
      mockOnChange.mockImplementation((newSelected) => {
        selected = newSelected
      })

      const button = screen.getByText(
        aesthetic.charAt(0).toUpperCase() + aesthetic.slice(1)
      ).closest('button')!
      await user.click(button)

      rerender(<AestheticsSelector selected={selected} onChange={mockOnChange} />)
    }

    expect(selected).toEqual(['minimalist', 'professional', 'playful'])
    expect(screen.getByText('3/3 selected')).toBeInTheDocument()
  })
})

describe('AestheticsSelector - Error Display', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('should display error message when provided', () => {
    render(
      <AestheticsSelector
        selected={[]}
        onChange={mockOnChange}
        error="Select at least one aesthetic"
      />
    )

    expect(screen.getByText('Select at least one aesthetic')).toBeInTheDocument()
  })

  it('should not display error when not provided', () => {
    render(<AestheticsSelector selected={[]} onChange={mockOnChange} />)

    // Error text should not be present
    const errorElements = screen.queryAllByText(/Select at least/i)
    expect(errorElements).toHaveLength(0)
  })
})
