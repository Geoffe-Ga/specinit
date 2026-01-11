import { render, screen } from '@testing-library/react'
import { describe, it, expect } from 'vitest'

import { LoadingState } from '../LoadingState'

describe('LoadingState', () => {
  it('should render loading message', () => {
    render(<LoadingState />)
    expect(screen.getByText(/generating tech stack recommendations/i)).toBeInTheDocument()
  })
})
