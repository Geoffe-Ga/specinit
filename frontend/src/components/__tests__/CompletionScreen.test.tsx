import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { CompletionScreen } from '../CompletionScreen'
import type { GenerationResult } from '../../types'

describe('CompletionScreen', () => {
  const mockOnNewProject = vi.fn()

  const mockResult: GenerationResult = {
    path: '/Users/test/my-project',
    totalCost: 1.25,
    generationTime: 45,
  }

  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('Rendering', () => {
    it('should render success message', () => {
      render(<CompletionScreen result={mockResult} onNewProject={mockOnNewProject} />)

      expect(screen.getByText('Project Complete!')).toBeInTheDocument()
      expect(
        screen.getByText('Your project has been successfully generated.')
      ).toBeInTheDocument()
    })

    it('should render project location', () => {
      render(<CompletionScreen result={mockResult} onNewProject={mockOnNewProject} />)

      expect(screen.getByText('Location')).toBeInTheDocument()
      expect(screen.getByText('/Users/test/my-project')).toBeInTheDocument()
    })

    it('should render total cost with dollar sign', () => {
      render(<CompletionScreen result={mockResult} onNewProject={mockOnNewProject} />)

      expect(screen.getByText('Total Cost')).toBeInTheDocument()
      expect(screen.getByText('$1.25')).toBeInTheDocument()
    })

    it('should render generation time', () => {
      render(<CompletionScreen result={mockResult} onNewProject={mockOnNewProject} />)

      expect(screen.getByText('Generation Time')).toBeInTheDocument()
      expect(screen.getByText('45s')).toBeInTheDocument()
    })

    it('should render new project button', () => {
      render(<CompletionScreen result={mockResult} onNewProject={mockOnNewProject} />)

      expect(screen.getByRole('button', { name: 'Create Another Project' })).toBeInTheDocument()
    })
  })

  describe('Time Formatting', () => {
    it('should format time in seconds when less than 60 seconds', () => {
      const result = { ...mockResult, generationTime: 30 }
      render(<CompletionScreen result={result} onNewProject={mockOnNewProject} />)

      expect(screen.getByText('30s')).toBeInTheDocument()
    })

    it('should format time in minutes and seconds when 60 seconds or more', () => {
      const result = { ...mockResult, generationTime: 90 }
      render(<CompletionScreen result={result} onNewProject={mockOnNewProject} />)

      expect(screen.getByText('1m 30s')).toBeInTheDocument()
    })

    it('should round seconds correctly', () => {
      const result = { ...mockResult, generationTime: 45.7 }
      render(<CompletionScreen result={result} onNewProject={mockOnNewProject} />)

      expect(screen.getByText('46s')).toBeInTheDocument()
    })

    it('should handle exact minute boundaries', () => {
      const result = { ...mockResult, generationTime: 120 }
      render(<CompletionScreen result={result} onNewProject={mockOnNewProject} />)

      expect(screen.getByText('2m 0s')).toBeInTheDocument()
    })

    it('should handle large time values', () => {
      const result = { ...mockResult, generationTime: 305 }
      render(<CompletionScreen result={result} onNewProject={mockOnNewProject} />)

      expect(screen.getByText('5m 5s')).toBeInTheDocument()
    })
  })

  describe('Cost Formatting', () => {
    it('should format cost with 2 decimal places', () => {
      const result = { ...mockResult, totalCost: 0.5 }
      render(<CompletionScreen result={result} onNewProject={mockOnNewProject} />)

      expect(screen.getByText('$0.50')).toBeInTheDocument()
    })

    it('should handle zero cost', () => {
      const result = { ...mockResult, totalCost: 0 }
      render(<CompletionScreen result={result} onNewProject={mockOnNewProject} />)

      expect(screen.getByText('$0.00')).toBeInTheDocument()
    })

    it('should handle large costs', () => {
      const result = { ...mockResult, totalCost: 15.99 }
      render(<CompletionScreen result={result} onNewProject={mockOnNewProject} />)

      expect(screen.getByText('$15.99')).toBeInTheDocument()
    })
  })

  describe('Next Steps', () => {
    it('should display next steps with project folder name', () => {
      render(<CompletionScreen result={mockResult} onNewProject={mockOnNewProject} />)

      expect(screen.getByText(/cd my-project/)).toBeInTheDocument()
      expect(screen.getByText(/npm install/)).toBeInTheDocument()
      expect(screen.getByText(/npm run dev/)).toBeInTheDocument()
    })

    it('should extract folder name from full path', () => {
      const result = { ...mockResult, path: '/Users/test/workspace/react-app' }
      render(<CompletionScreen result={result} onNewProject={mockOnNewProject} />)

      expect(screen.getByText(/cd react-app/)).toBeInTheDocument()
    })

    it('should show alternative commands in comments', () => {
      render(<CompletionScreen result={mockResult} onNewProject={mockOnNewProject} />)

      expect(screen.getByText(/# or pip install -e ./)).toBeInTheDocument()
      expect(screen.getByText(/# or python -m your_app/)).toBeInTheDocument()
    })
  })

  describe('New Project Button', () => {
    it('should call onNewProject when button is clicked', async () => {
      const user = userEvent.setup()
      render(<CompletionScreen result={mockResult} onNewProject={mockOnNewProject} />)

      const button = screen.getByRole('button', { name: 'Create Another Project' })
      await user.click(button)

      expect(mockOnNewProject).toHaveBeenCalledTimes(1)
    })
  })
})
