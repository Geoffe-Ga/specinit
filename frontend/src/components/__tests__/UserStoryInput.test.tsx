import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '../../test/test-utils'
import { UserStoryInput } from '../UserStoryInput'
import userEvent from '@testing-library/user-event'

// Mock useSuggestionContext
vi.mock('../../contexts/SuggestionContext', async (importOriginal) => {
  const actual = await importOriginal<typeof import('../../contexts/SuggestionContext')>()
  return {
    ...actual,
    useSuggestionContext: vi.fn(() => ({
      suggestionsEnabled: false,
      getSuggestions: vi.fn(),
      isLoading: false,
    })),
  }
})

describe('UserStoryInput', () => {
  const mockOnChange = vi.fn()
  const defaultValue = {
    role: '',
    action: '',
    outcome: '',
  }

  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('Manual Input', () => {
    it('should render all three input fields', () => {
      render(<UserStoryInput value={defaultValue} onChange={mockOnChange} />)

      expect(screen.getByPlaceholderText('a developer')).toBeInTheDocument()
      expect(screen.getByPlaceholderText('quickly bootstrap new projects')).toBeInTheDocument()
      expect(screen.getByPlaceholderText('I can focus on building features')).toBeInTheDocument()
    })

    it('should display current values in inputs', () => {
      const value = {
        role: 'developer',
        action: 'write tests',
        outcome: 'ensure quality',
      }

      render(<UserStoryInput value={value} onChange={mockOnChange} />)

      expect(screen.getByDisplayValue('developer')).toBeInTheDocument()
      expect(screen.getByDisplayValue('write tests')).toBeInTheDocument()
      expect(screen.getByDisplayValue('ensure quality')).toBeInTheDocument()
    })

    it('should call onChange when role input changes', async () => {
      const user = userEvent.setup()
      render(<UserStoryInput value={defaultValue} onChange={mockOnChange} />)

      const roleInput = screen.getByPlaceholderText('a developer')
      await user.type(roleInput, 'tester')

      await waitFor(() => {
        expect(mockOnChange).toHaveBeenCalled()
      })
    })

    it('should call onChange when action input changes', async () => {
      const user = userEvent.setup()
      render(<UserStoryInput value={defaultValue} onChange={mockOnChange} />)

      const actionInput = screen.getByPlaceholderText('quickly bootstrap new projects')
      await user.type(actionInput, 'verify functionality')

      await waitFor(() => {
        expect(mockOnChange).toHaveBeenCalled()
      })
    })

    it('should call onChange when outcome input changes', async () => {
      const user = userEvent.setup()
      render(<UserStoryInput value={defaultValue} onChange={mockOnChange} />)

      const outcomeInput = screen.getByPlaceholderText('I can focus on building features')
      await user.type(outcomeInput, 'deliver quality software')

      await waitFor(() => {
        expect(mockOnChange).toHaveBeenCalled()
      })
    })
  })

  describe('Error Display', () => {
    it('should display error for role field', () => {
      const errors = {
        role: { message: 'Role is required', type: 'required' },
      }

      render(<UserStoryInput value={defaultValue} onChange={mockOnChange} errors={errors} />)

      expect(screen.getByText('Role is required')).toBeInTheDocument()
    })

    it('should display error for action field', () => {
      const errors = {
        action: { message: 'Action is required', type: 'required' },
      }

      render(<UserStoryInput value={defaultValue} onChange={mockOnChange} errors={errors} />)

      expect(screen.getByText('Action is required')).toBeInTheDocument()
    })

    it('should display error for outcome field', () => {
      const errors = {
        outcome: { message: 'Outcome is required', type: 'required' },
      }

      render(<UserStoryInput value={defaultValue} onChange={mockOnChange} errors={errors} />)

      expect(screen.getByText('Outcome is required')).toBeInTheDocument()
    })

    it('should display multiple errors at once', () => {
      const errors = {
        role: { message: 'Role is required', type: 'required' },
        action: { message: 'Action is required', type: 'required' },
        outcome: { message: 'Outcome is required', type: 'required' },
      }

      render(<UserStoryInput value={defaultValue} onChange={mockOnChange} errors={errors} />)

      expect(screen.getByText('Role is required')).toBeInTheDocument()
      expect(screen.getByText('Action is required')).toBeInTheDocument()
      expect(screen.getByText('Outcome is required')).toBeInTheDocument()
    })
  })
})
