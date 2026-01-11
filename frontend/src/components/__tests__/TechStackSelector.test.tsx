import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, it, expect, vi, beforeEach } from 'vitest'

import type { TechStack } from '../../types'
import { TechStackSelector } from '../TechStackSelector'

const mockOnChange = vi.fn()
const emptyTechStack: TechStack = { frontend: [], backend: [], database: [], tools: [] }
const PLATFORMS_WEB = ['web']
const PLATFORMS_CLI = ['cli']
const PLATFORMS_API = ['api']

describe('TechStackSelector - Rendering', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('should render all sections for web platform', () => {
    render(
      <TechStackSelector value={emptyTechStack} onChange={mockOnChange} platforms={PLATFORMS_WEB} />
    )

    expect(screen.getByText('Frontend')).toBeInTheDocument()
    expect(screen.getByText('Backend')).toBeInTheDocument()
    expect(screen.getByText('Database')).toBeInTheDocument()
    expect(screen.getByText('Tools')).toBeInTheDocument()
  })

  it('should render frontend options', () => {
    render(
      <TechStackSelector value={emptyTechStack} onChange={mockOnChange} platforms={PLATFORMS_WEB} />
    )

    expect(screen.getByRole('button', { name: 'React' })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Vue' })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'TypeScript' })).toBeInTheDocument()
  })

  it('should render backend options', () => {
    render(
      <TechStackSelector value={emptyTechStack} onChange={mockOnChange} platforms={PLATFORMS_WEB} />
    )

    expect(screen.getByRole('button', { name: 'FastAPI' })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Django' })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Node.js' })).toBeInTheDocument()
  })

  it('should render database and tools options', () => {
    render(
      <TechStackSelector value={emptyTechStack} onChange={mockOnChange} platforms={PLATFORMS_WEB} />
    )

    expect(screen.getByRole('button', { name: 'PostgreSQL' })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'ESLint' })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Docker' })).toBeInTheDocument()
  })
})

describe('TechStackSelector - Selection State', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('should show selected options with blue background', () => {
    const techStack: TechStack = {
      frontend: ['React'],
      backend: ['FastAPI'],
      database: [],
      tools: [],
    }

    render(<TechStackSelector value={techStack} onChange={mockOnChange} platforms={PLATFORMS_WEB} />)

    expect(screen.getByRole('button', { name: 'React' })).toHaveClass('bg-blue-600', 'text-white')
    expect(screen.getByRole('button', { name: 'FastAPI' })).toHaveClass('bg-blue-600', 'text-white')
  })

  it('should show unselected options with gray background', () => {
    render(
      <TechStackSelector value={emptyTechStack} onChange={mockOnChange} platforms={PLATFORMS_WEB} />
    )

    expect(screen.getByRole('button', { name: 'Vue' })).toHaveClass('bg-gray-100', 'text-gray-700')
  })
})

describe('TechStackSelector - Toggle Behavior', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('should add option when clicking unselected', async () => {
    const user = userEvent.setup()
    render(
      <TechStackSelector value={emptyTechStack} onChange={mockOnChange} platforms={PLATFORMS_WEB} />
    )

    await user.click(screen.getByRole('button', { name: 'React' }))

    expect(mockOnChange).toHaveBeenCalledWith({
      frontend: ['React'],
      backend: [],
      database: [],
      tools: [],
    })
  })

  it('should remove option when clicking selected', async () => {
    const user = userEvent.setup()
    const techStack: TechStack = {
      frontend: ['React', 'TypeScript'],
      backend: [],
      database: [],
      tools: [],
    }

    render(<TechStackSelector value={techStack} onChange={mockOnChange} platforms={PLATFORMS_WEB} />)
    await user.click(screen.getByRole('button', { name: 'React' }))

    expect(mockOnChange).toHaveBeenCalledWith({
      frontend: ['TypeScript'],
      backend: [],
      database: [],
      tools: [],
    })
  })

  it('should preserve other categories when toggling', async () => {
    const user = userEvent.setup()
    const techStack: TechStack = {
      frontend: ['React'],
      backend: ['FastAPI'],
      database: ['PostgreSQL'],
      tools: [],
    }

    render(<TechStackSelector value={techStack} onChange={mockOnChange} platforms={PLATFORMS_WEB} />)
    await user.click(screen.getByRole('button', { name: 'PostgreSQL' }))

    expect(mockOnChange).toHaveBeenCalledWith({
      frontend: ['React'],
      backend: ['FastAPI'],
      database: [],
      tools: [],
    })
  })
})

describe('TechStackSelector - Platform Rendering', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('should show frontend and backend for web platform', () => {
    render(
      <TechStackSelector value={emptyTechStack} onChange={mockOnChange} platforms={PLATFORMS_WEB} />
    )
    expect(screen.getByText('Frontend')).toBeInTheDocument()
    expect(screen.getByText('Backend')).toBeInTheDocument()
  })

  it('should not show frontend or backend for cli platform', () => {
    render(
      <TechStackSelector value={emptyTechStack} onChange={mockOnChange} platforms={PLATFORMS_CLI} />
    )
    expect(screen.queryByText('Frontend')).not.toBeInTheDocument()
    expect(screen.queryByText('Backend')).not.toBeInTheDocument()
  })

  it('should show backend for api platform', () => {
    render(
      <TechStackSelector value={emptyTechStack} onChange={mockOnChange} platforms={PLATFORMS_API} />
    )
    expect(screen.getByText('Backend')).toBeInTheDocument()
  })

  it('should always show database and tools sections', () => {
    render(
      <TechStackSelector value={emptyTechStack} onChange={mockOnChange} platforms={PLATFORMS_CLI} />
    )
    expect(screen.getByText('Database')).toBeInTheDocument()
    expect(screen.getByText('Tools')).toBeInTheDocument()
  })
})
