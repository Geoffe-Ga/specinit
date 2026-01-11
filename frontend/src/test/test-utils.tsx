import { render, RenderOptions, screen, waitFor, within } from '@testing-library/react'
import { ReactElement } from 'react'

import { SuggestionProvider } from '../contexts/SuggestionContext'

// Custom render function that includes providers
function customRender(ui: ReactElement, options?: Omit<RenderOptions, 'wrapper'>) {
  return render(ui, {
    wrapper: ({ children }) => <SuggestionProvider>{children}</SuggestionProvider>,
    ...options,
  })
}

// Export custom render and commonly used utilities
export { customRender as render, screen, waitFor, within }
