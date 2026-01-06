import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { PlatformSelector } from '../PlatformSelector'

describe('PlatformSelector', () => {
  const mockOnChange = vi.fn()

  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('Rendering', () => {
    it('should render all platform options', () => {
      render(<PlatformSelector selected={[]} onChange={mockOnChange} />)

      expect(screen.getByText('Web')).toBeInTheDocument()
      expect(screen.getByText('iOS')).toBeInTheDocument()
      expect(screen.getByText('Android')).toBeInTheDocument()
      expect(screen.getByText('Desktop')).toBeInTheDocument()
      expect(screen.getByText('CLI')).toBeInTheDocument()
      expect(screen.getByText('API/Backend')).toBeInTheDocument()
    })

    it('should render platform icons', () => {
      render(<PlatformSelector selected={[]} onChange={mockOnChange} />)

      // Icons are rendered as text emojis
      expect(screen.getByText('🌐')).toBeInTheDocument()
      expect(screen.getByText('📱')).toBeInTheDocument()
      expect(screen.getByText('🤖')).toBeInTheDocument()
      expect(screen.getByText('🖥️')).toBeInTheDocument()
      expect(screen.getByText('⌨️')).toBeInTheDocument()
      expect(screen.getByText('🔌')).toBeInTheDocument()
    })

    it('should render the label', () => {
      render(<PlatformSelector selected={[]} onChange={mockOnChange} />)

      expect(screen.getByText('Target Platforms')).toBeInTheDocument()
    })
  })

  describe('Selection State', () => {
    it('should show selected platforms with different styling', () => {
      render(<PlatformSelector selected={['web', 'ios']} onChange={mockOnChange} />)

      const webButton = screen.getByText('Web').closest('button')
      const iosButton = screen.getByText('iOS').closest('button')
      const androidButton = screen.getByText('Android').closest('button')

      // Selected items should have blue border
      expect(webButton).toHaveClass('border-blue-500')
      expect(iosButton).toHaveClass('border-blue-500')
      // Unselected should have gray border
      expect(androidButton).toHaveClass('border-gray-200')
    })
  })

  describe('Toggle Behavior', () => {
    it('should add platform when clicking unselected', async () => {
      const user = userEvent.setup()
      render(<PlatformSelector selected={[]} onChange={mockOnChange} />)

      const webButton = screen.getByText('Web').closest('button')!
      await user.click(webButton)

      expect(mockOnChange).toHaveBeenCalledWith(['web'])
    })

    it('should remove platform when clicking selected', async () => {
      const user = userEvent.setup()
      render(<PlatformSelector selected={['web', 'ios']} onChange={mockOnChange} />)

      const webButton = screen.getByText('Web').closest('button')!
      await user.click(webButton)

      expect(mockOnChange).toHaveBeenCalledWith(['ios'])
    })

    it('should preserve other selections when adding', async () => {
      const user = userEvent.setup()
      render(<PlatformSelector selected={['web']} onChange={mockOnChange} />)

      const iosButton = screen.getByText('iOS').closest('button')!
      await user.click(iosButton)

      expect(mockOnChange).toHaveBeenCalledWith(['web', 'ios'])
    })

    it('should preserve other selections when removing', async () => {
      const user = userEvent.setup()
      render(<PlatformSelector selected={['web', 'ios', 'android']} onChange={mockOnChange} />)

      const iosButton = screen.getByText('iOS').closest('button')!
      await user.click(iosButton)

      expect(mockOnChange).toHaveBeenCalledWith(['web', 'android'])
    })

    it('should allow selecting all platforms', async () => {
      const user = userEvent.setup()
      const { rerender } = render(<PlatformSelector selected={[]} onChange={mockOnChange} />)

      // Click all platforms sequentially
      const platforms = ['web', 'ios', 'android', 'desktop', 'cli', 'api']
      let selected: string[] = []

      for (const platform of platforms) {
        mockOnChange.mockImplementation((newSelected) => {
          selected = newSelected
        })

        // Map platform IDs to their display text
        const platformDisplayText: Record<string, string> = {
          'web': 'Web',
          'ios': 'iOS',
          'android': 'Android',
          'desktop': 'Desktop',
          'cli': 'CLI',
          'api': 'API/Backend'
        }

        const displayText = platformDisplayText[platform]
        const button = screen.getByText(displayText).closest('button')!
        await user.click(button)

        rerender(<PlatformSelector selected={selected} onChange={mockOnChange} />)
      }

      expect(selected).toEqual(['web', 'ios', 'android', 'desktop', 'cli', 'api'])
    })
  })

  describe('Error Display', () => {
    it('should display error message when provided', () => {
      render(
        <PlatformSelector
          selected={[]}
          onChange={mockOnChange}
          error="Select at least one platform"
        />
      )

      expect(screen.getByText('Select at least one platform')).toBeInTheDocument()
    })

    it('should not display error when not provided', () => {
      render(<PlatformSelector selected={[]} onChange={mockOnChange} />)

      expect(screen.queryByRole('alert')).not.toBeInTheDocument()
    })
  })
})
