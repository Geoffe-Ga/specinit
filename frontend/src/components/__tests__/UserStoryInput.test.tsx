import userEvent from '@testing-library/user-event'
import { describe, it, expect, vi, beforeEach } from 'vitest'

import { render, screen, waitFor } from '../../test/test-utils'
import { UserStoryInput } from '../UserStoryInput'

// Test constants
const ERROR_MESSAGES = {
  ROLE_REQUIRED: 'Role is required',
  ACTION_REQUIRED: 'Action is required',
  OUTCOME_REQUIRED: 'Outcome is required',
}

const mockOnChange = vi.fn()
const defaultValue = {
  role: '',
  action: '',
  outcome: '',
}

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

describe('UserStoryInput - Manual Input', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

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

describe('UserStoryInput - Error Display', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('should display error for role field', () => {
    const errors = {
      role: { message: ERROR_MESSAGES.ROLE_REQUIRED, type: 'required' },
    }

    render(<UserStoryInput value={defaultValue} onChange={mockOnChange} errors={errors} />)

    expect(screen.getByText(ERROR_MESSAGES.ROLE_REQUIRED)).toBeInTheDocument()
  })

  it('should display error for action field', () => {
    const errors = {
      action: { message: ERROR_MESSAGES.ACTION_REQUIRED, type: 'required' },
    }

    render(<UserStoryInput value={defaultValue} onChange={mockOnChange} errors={errors} />)

    expect(screen.getByText(ERROR_MESSAGES.ACTION_REQUIRED)).toBeInTheDocument()
  })

  it('should display error for outcome field', () => {
    const errors = {
      outcome: { message: ERROR_MESSAGES.OUTCOME_REQUIRED, type: 'required' },
    }

    render(<UserStoryInput value={defaultValue} onChange={mockOnChange} errors={errors} />)

    expect(screen.getByText(ERROR_MESSAGES.OUTCOME_REQUIRED)).toBeInTheDocument()
  })

  it('should display multiple errors at once', () => {
    const errors = {
      role: { message: ERROR_MESSAGES.ROLE_REQUIRED, type: 'required' },
      action: { message: ERROR_MESSAGES.ACTION_REQUIRED, type: 'required' },
      outcome: { message: ERROR_MESSAGES.OUTCOME_REQUIRED, type: 'required' },
    }

    render(<UserStoryInput value={defaultValue} onChange={mockOnChange} errors={errors} />)

    expect(screen.getByText(ERROR_MESSAGES.ROLE_REQUIRED)).toBeInTheDocument()
    expect(screen.getByText(ERROR_MESSAGES.ACTION_REQUIRED)).toBeInTheDocument()
    expect(screen.getByText(ERROR_MESSAGES.OUTCOME_REQUIRED)).toBeInTheDocument()
  })
})
