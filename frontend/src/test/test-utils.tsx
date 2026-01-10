import { ReactElement } from 'react'
import { render, RenderOptions } from '@testing-library/react'
import { SuggestionProvider } from '../contexts/SuggestionContext'

// Custom render function that includes providers
function customRender(ui: ReactElement, options?: Omit<RenderOptions, 'wrapper'>) {
  return render(ui, {
    wrapper: ({ children }) => <SuggestionProvider>{children}</SuggestionProvider>,
    ...options,
  })
}

// Re-export everything
// eslint-disable-next-line react-refresh/only-export-components
export * from '@testing-library/react'
export { customRender as render }
