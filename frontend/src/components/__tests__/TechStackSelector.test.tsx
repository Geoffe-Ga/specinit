import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { TechStackSelector } from '../TechStackSelector'
import type { TechStack } from '../../types'

describe('TechStackSelector', () => {
  const mockOnChange = vi.fn()

  const emptyTechStack: TechStack = {
    frontend: [],
    backend: [],
    database: [],
    tools: [],
  }

  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('Rendering', () => {
    it('should render frontend section when web platform is selected', () => {
      render(
        <TechStackSelector value={emptyTechStack} onChange={mockOnChange} platforms={['web']} />
      )

      expect(screen.getByText('Frontend')).toBeInTheDocument()
      expect(screen.getByRole('button', { name: 'React' })).toBeInTheDocument()
      expect(screen.getByRole('button', { name: 'Vue' })).toBeInTheDocument()
      expect(screen.getByRole('button', { name: 'TypeScript' })).toBeInTheDocument()
    })

    it('should render backend section when non-cli platform is selected', () => {
      render(
        <TechStackSelector value={emptyTechStack} onChange={mockOnChange} platforms={['web']} />
      )

      expect(screen.getByText('Backend')).toBeInTheDocument()
      expect(screen.getByRole('button', { name: 'FastAPI' })).toBeInTheDocument()
      expect(screen.getByRole('button', { name: 'Express' })).toBeInTheDocument()
      expect(screen.getByRole('button', { name: 'Django' })).toBeInTheDocument()
    })

    it('should render database section', () => {
      render(
        <TechStackSelector value={emptyTechStack} onChange={mockOnChange} platforms={['web']} />
      )

      expect(screen.getByText('Database')).toBeInTheDocument()
      expect(screen.getByRole('button', { name: 'PostgreSQL' })).toBeInTheDocument()
      expect(screen.getByRole('button', { name: 'MongoDB' })).toBeInTheDocument()
      expect(screen.getByRole('button', { name: 'SQLite' })).toBeInTheDocument()
    })

    it('should render tools section', () => {
      render(
        <TechStackSelector value={emptyTechStack} onChange={mockOnChange} platforms={['web']} />
      )

      expect(screen.getByText('Tools')).toBeInTheDocument()
      expect(screen.getByRole('button', { name: 'ESLint' })).toBeInTheDocument()
      expect(screen.getByRole('button', { name: 'Prettier' })).toBeInTheDocument()
      expect(screen.getByRole('button', { name: 'Jest' })).toBeInTheDocument()
    })

    it('should render all tech options in their respective categories', () => {
      render(
        <TechStackSelector value={emptyTechStack} onChange={mockOnChange} platforms={['web']} />
      )

      // Frontend options
      expect(screen.getByRole('button', { name: 'React' })).toBeInTheDocument()
      expect(screen.getByRole('button', { name: 'Vue' })).toBeInTheDocument()
      expect(screen.getByRole('button', { name: 'Svelte' })).toBeInTheDocument()
      expect(screen.getByRole('button', { name: 'Next.js' })).toBeInTheDocument()
      expect(screen.getByRole('button', { name: 'React Native' })).toBeInTheDocument()
      expect(screen.getByRole('button', { name: 'TypeScript' })).toBeInTheDocument()

      // Backend options
      expect(screen.getByRole('button', { name: 'FastAPI' })).toBeInTheDocument()
      expect(screen.getByRole('button', { name: 'Express' })).toBeInTheDocument()
      expect(screen.getByRole('button', { name: 'Django' })).toBeInTheDocument()
      expect(screen.getByRole('button', { name: 'Node.js' })).toBeInTheDocument()
      expect(screen.getByRole('button', { name: 'Python' })).toBeInTheDocument()

      // Database options
      expect(screen.getByRole('button', { name: 'PostgreSQL' })).toBeInTheDocument()
      expect(screen.getByRole('button', { name: 'MongoDB' })).toBeInTheDocument()
      expect(screen.getByRole('button', { name: 'SQLite' })).toBeInTheDocument()
      expect(screen.getByRole('button', { name: 'Supabase' })).toBeInTheDocument()
      expect(screen.getByRole('button', { name: 'Firebase' })).toBeInTheDocument()

      // Tools options
      expect(screen.getByRole('button', { name: 'ESLint' })).toBeInTheDocument()
      expect(screen.getByRole('button', { name: 'Prettier' })).toBeInTheDocument()
      expect(screen.getByRole('button', { name: 'Jest' })).toBeInTheDocument()
      expect(screen.getByRole('button', { name: 'pytest' })).toBeInTheDocument()
      expect(screen.getByRole('button', { name: 'Docker' })).toBeInTheDocument()
    })
  })

  describe('Selection State', () => {
    it('should show selected options with blue background', () => {
      const techStack: TechStack = {
        frontend: ['React', 'TypeScript'],
        backend: ['FastAPI'],
        database: ['PostgreSQL'],
        tools: ['ESLint'],
      }

      render(<TechStackSelector value={techStack} onChange={mockOnChange} platforms={['web']} />)

      const reactButton = screen.getByRole('button', { name: 'React' })
      const fastAPIButton = screen.getByRole('button', { name: 'FastAPI' })

      expect(reactButton).toHaveClass('bg-blue-600', 'text-white')
      expect(fastAPIButton).toHaveClass('bg-blue-600', 'text-white')
    })

    it('should show unselected options with gray background', () => {
      const techStack: TechStack = {
        frontend: ['React'],
        backend: [],
        database: [],
        tools: [],
      }

      render(<TechStackSelector value={techStack} onChange={mockOnChange} platforms={['web']} />)

      const vueButton = screen.getByRole('button', { name: 'Vue' })
      const djangoButton = screen.getByRole('button', { name: 'Django' })

      expect(vueButton).toHaveClass('bg-gray-100', 'text-gray-700')
      expect(djangoButton).toHaveClass('bg-gray-100', 'text-gray-700')
    })
  })

  describe('Toggle Behavior', () => {
    it('should add option when clicking unselected frontend option', async () => {
      const user = userEvent.setup()
      render(
        <TechStackSelector value={emptyTechStack} onChange={mockOnChange} platforms={['web']} />
      )

      const reactButton = screen.getByRole('button', { name: 'React' })
      await user.click(reactButton)

      expect(mockOnChange).toHaveBeenCalledWith({
        frontend: ['React'],
        backend: [],
        database: [],
        tools: [],
      })
    })

    it('should remove option when clicking selected frontend option', async () => {
      const user = userEvent.setup()
      const techStack: TechStack = {
        frontend: ['React', 'TypeScript'],
        backend: [],
        database: [],
        tools: [],
      }

      render(<TechStackSelector value={techStack} onChange={mockOnChange} platforms={['web']} />)

      const reactButton = screen.getByRole('button', { name: 'React' })
      await user.click(reactButton)

      expect(mockOnChange).toHaveBeenCalledWith({
        frontend: ['TypeScript'],
        backend: [],
        database: [],
        tools: [],
      })
    })

    it('should preserve other selections when adding backend option', async () => {
      const user = userEvent.setup()
      const techStack: TechStack = {
        frontend: ['React'],
        backend: [],
        database: [],
        tools: [],
      }

      render(<TechStackSelector value={techStack} onChange={mockOnChange} platforms={['web']} />)

      const fastAPIButton = screen.getByRole('button', { name: 'FastAPI' })
      await user.click(fastAPIButton)

      expect(mockOnChange).toHaveBeenCalledWith({
        frontend: ['React'],
        backend: ['FastAPI'],
        database: [],
        tools: [],
      })
    })

    it('should preserve other selections when removing database option', async () => {
      const user = userEvent.setup()
      const techStack: TechStack = {
        frontend: ['React'],
        backend: ['FastAPI'],
        database: ['PostgreSQL', 'MongoDB'],
        tools: ['ESLint'],
      }

      render(<TechStackSelector value={techStack} onChange={mockOnChange} platforms={['web']} />)

      const postgresButton = screen.getByRole('button', { name: 'PostgreSQL' })
      await user.click(postgresButton)

      expect(mockOnChange).toHaveBeenCalledWith({
        frontend: ['React'],
        backend: ['FastAPI'],
        database: ['MongoDB'],
        tools: ['ESLint'],
      })
    })

    it('should allow selecting multiple options in same category', async () => {
      const user = userEvent.setup()
      let currentTechStack = emptyTechStack
      const { rerender } = render(
        <TechStackSelector value={currentTechStack} onChange={mockOnChange} platforms={['web']} />
      )

      mockOnChange.mockImplementation((newTechStack) => {
        currentTechStack = newTechStack
      })

      const eslintButton = screen.getByRole('button', { name: 'ESLint' })
      await user.click(eslintButton)
      rerender(
        <TechStackSelector value={currentTechStack} onChange={mockOnChange} platforms={['web']} />
      )

      const prettierButton = screen.getByRole('button', { name: 'Prettier' })
      await user.click(prettierButton)

      // Check the final state includes both
      expect(currentTechStack.tools).toEqual(['ESLint', 'Prettier'])
    })
  })

  describe('Conditional Rendering', () => {
    it('should show frontend for web platform', () => {
      render(
        <TechStackSelector value={emptyTechStack} onChange={mockOnChange} platforms={['web']} />
      )

      expect(screen.getByText('Frontend')).toBeInTheDocument()
    })

    it('should show frontend for ios platform', () => {
      render(
        <TechStackSelector value={emptyTechStack} onChange={mockOnChange} platforms={['ios']} />
      )

      expect(screen.getByText('Frontend')).toBeInTheDocument()
    })

    it('should show frontend for android platform', () => {
      render(
        <TechStackSelector
          value={emptyTechStack}
          onChange={mockOnChange}
          platforms={['android']}
        />
      )

      expect(screen.getByText('Frontend')).toBeInTheDocument()
    })

    it('should show frontend for desktop platform', () => {
      render(
        <TechStackSelector
          value={emptyTechStack}
          onChange={mockOnChange}
          platforms={['desktop']}
        />
      )

      expect(screen.getByText('Frontend')).toBeInTheDocument()
    })

    it('should not show frontend for cli-only platform', () => {
      render(
        <TechStackSelector value={emptyTechStack} onChange={mockOnChange} platforms={['cli']} />
      )

      expect(screen.queryByText('Frontend')).not.toBeInTheDocument()
    })

    it('should not show backend for cli-only platform', () => {
      render(
        <TechStackSelector value={emptyTechStack} onChange={mockOnChange} platforms={['cli']} />
      )

      expect(screen.queryByText('Backend')).not.toBeInTheDocument()
    })

    it('should show backend for api platform', () => {
      render(
        <TechStackSelector value={emptyTechStack} onChange={mockOnChange} platforms={['api']} />
      )

      expect(screen.getByText('Backend')).toBeInTheDocument()
    })

    it('should always show database section', () => {
      render(
        <TechStackSelector value={emptyTechStack} onChange={mockOnChange} platforms={['cli']} />
      )

      expect(screen.getByText('Database')).toBeInTheDocument()
    })

    it('should always show tools section', () => {
      render(
        <TechStackSelector value={emptyTechStack} onChange={mockOnChange} platforms={['cli']} />
      )

      expect(screen.getByText('Tools')).toBeInTheDocument()
    })

    it('should show frontend when multiple platforms include web', () => {
      render(
        <TechStackSelector
          value={emptyTechStack}
          onChange={mockOnChange}
          platforms={['web', 'api']}
        />
      )

      expect(screen.getByText('Frontend')).toBeInTheDocument()
      expect(screen.getByText('Backend')).toBeInTheDocument()
    })
  })
})
