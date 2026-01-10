import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { FeatureList } from '../FeatureList'

describe('FeatureList', () => {
  const mockOnChange = vi.fn()

  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('Rendering', () => {
    it('should render feature fields for each feature', () => {
      render(<FeatureList features={['Feature 1', 'Feature 2']} onChange={mockOnChange} />)

      // Check that both textareas are rendered with correct values
      const textareas = screen.getAllByRole('textbox')
      expect(textareas).toHaveLength(2)
      expect(screen.getByDisplayValue('Feature 1')).toBeInTheDocument()
      expect(screen.getByDisplayValue('Feature 2')).toBeInTheDocument()
    })

    it('should render placeholder text', () => {
      render(<FeatureList features={['']} onChange={mockOnChange} />)

      expect(
        screen.getByPlaceholderText(
          /Describe this feature \(1-2 words for simple features, or write detailed requirements\).../
        )
      ).toBeInTheDocument()
    })

    it('should display character count', () => {
      render(<FeatureList features={['User authentication']} onChange={mockOnChange} />)

      expect(screen.getByText('19 / 2000 characters')).toBeInTheDocument()
    })

    it('should display word count', () => {
      render(<FeatureList features={['User authentication system']} onChange={mockOnChange} />)

      expect(screen.getByText('3 words')).toBeInTheDocument()
    })

    it('should display singular word for single word', () => {
      render(<FeatureList features={['Authentication']} onChange={mockOnChange} />)

      expect(screen.getByText('1 word')).toBeInTheDocument()
    })

    it('should display 0 words for empty feature', () => {
      render(<FeatureList features={['']} onChange={mockOnChange} />)

      expect(screen.getByText('0 words')).toBeInTheDocument()
    })

    it('should display add feature button with count', () => {
      render(<FeatureList features={['Feature 1', 'Feature 2']} onChange={mockOnChange} />)

      expect(screen.getByText('Add Feature (2/20)')).toBeInTheDocument()
    })
  })

  describe('Add Feature', () => {
    it('should add empty feature when clicking add button', async () => {
      const user = userEvent.setup()
      render(<FeatureList features={['Feature 1']} onChange={mockOnChange} />)

      const addButton = screen.getByText(/Add Feature/)
      await user.click(addButton)

      expect(mockOnChange).toHaveBeenCalledWith(['Feature 1', ''])
    })

    it('should not add feature when maximum is reached', async () => {
      const user = userEvent.setup()
      const maxFeatures = Array(20).fill('Feature')
      render(<FeatureList features={maxFeatures} onChange={mockOnChange} />)

      const addButton = screen.getByText(/Add Feature/)
      expect(addButton).toBeDisabled()

      await user.click(addButton)
      expect(mockOnChange).not.toHaveBeenCalled()
    })

    it('should show correct count when approaching maximum', () => {
      const features = Array(19).fill('Feature')
      render(<FeatureList features={features} onChange={mockOnChange} />)

      expect(screen.getByText('Add Feature (19/20)')).toBeInTheDocument()
    })
  })

  describe('Remove Feature', () => {
    it('should remove feature when clicking remove button', async () => {
      const user = userEvent.setup()
      render(<FeatureList features={['Feature 1', 'Feature 2']} onChange={mockOnChange} />)

      // Find the second feature's remove button
      const featureFields = screen.getAllByRole('button', { name: /Remove feature/ })
      await user.click(featureFields[1])

      expect(mockOnChange).toHaveBeenCalledWith(['Feature 1'])
    })

    it('should not allow removing the last feature', () => {
      render(<FeatureList features={['Feature 1']} onChange={mockOnChange} />)

      const removeButton = screen.getByRole('button', { name: /Cannot remove the last feature/ })
      expect(removeButton).toBeDisabled()
    })

    it('should enable remove button when more than one feature', () => {
      render(<FeatureList features={['Feature 1', 'Feature 2']} onChange={mockOnChange} />)

      const removeButtons = screen.getAllByRole('button', { name: /Remove feature/ })
      expect(removeButtons[0]).not.toBeDisabled()
      expect(removeButtons[1]).not.toBeDisabled()
    })

    it('should preserve other features when removing', async () => {
      const user = userEvent.setup()
      render(
        <FeatureList features={['Feature 1', 'Feature 2', 'Feature 3']} onChange={mockOnChange} />
      )

      // Remove the middle feature
      const removeButtons = screen.getAllByRole('button', { name: /Remove feature/ })
      await user.click(removeButtons[1])

      expect(mockOnChange).toHaveBeenCalledWith(['Feature 1', 'Feature 3'])
    })
  })

  describe('Update Feature', () => {
    it('should update feature text when typing', async () => {
      const user = userEvent.setup()
      render(<FeatureList features={['']} onChange={mockOnChange} />)

      const textarea = screen.getByPlaceholderText(/Describe this feature/)
      await user.type(textarea, 'Test')

      // onChange should be called for each keystroke
      expect(mockOnChange).toHaveBeenCalledTimes(4)
      // Verify that the feature array is passed to onChange
      expect(mockOnChange.mock.calls[0][0]).toBeInstanceOf(Array)
      expect(mockOnChange.mock.calls[0][0]).toHaveLength(1)
    })

    it('should preserve other features when updating', async () => {
      const user = userEvent.setup()
      render(<FeatureList features={['Feature 1', 'Feature 2']} onChange={mockOnChange} />)

      const textareas = screen.getAllByRole('textbox')
      await user.clear(textareas[0])
      await user.type(textareas[0], 'Updated')

      // Check that Feature 2 is preserved
      const lastCall = mockOnChange.mock.calls[mockOnChange.mock.calls.length - 1]
      expect(lastCall[0][1]).toBe('Feature 2')
    })

    it('should enforce maximum character length', () => {
      render(<FeatureList features={['Test feature']} onChange={mockOnChange} />)

      const textarea = screen.getByRole('textbox') as HTMLTextAreaElement
      expect(textarea.maxLength).toBe(2000)
    })
  })

  describe('Error Display', () => {
    it('should display error message when provided', () => {
      render(
        <FeatureList
          features={['']}
          onChange={mockOnChange}
          error="At least one feature is required"
        />
      )

      expect(screen.getByText('At least one feature is required')).toBeInTheDocument()
    })

    it('should not display error when not provided', () => {
      render(<FeatureList features={['']} onChange={mockOnChange} />)

      const errorText = screen.queryByText(/required/i)
      expect(errorText).not.toBeInTheDocument()
    })
  })
})
