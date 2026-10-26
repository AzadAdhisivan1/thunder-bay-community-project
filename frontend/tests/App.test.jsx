import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import App from '../src/App.jsx'

describe('App', () => {
  it('shows the home page at /', () => {
    render(
      <MemoryRouter initialEntries={['/']}>
        <App />
      </MemoryRouter>,
    )
    expect(screen.getByText('Thunder Link')).toBeInTheDocument()
    expect(
      screen.getByRole('heading', { name: /find community services/i }),
    ).toBeInTheDocument()
  })

  it('shows a not-found message for unknown pages', () => {
    render(
      <MemoryRouter initialEntries={['/does-not-exist']}>
        <App />
      </MemoryRouter>,
    )
    expect(screen.getByText(/page not found/i)).toBeInTheDocument()
  })
})
