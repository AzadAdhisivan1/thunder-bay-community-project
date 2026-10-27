import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import CategoryList from '../src/components/CategoryList.jsx'
import { getCategories } from '../src/api/client.js'

vi.mock('../src/api/client.js', () => ({
  getCategories: vi.fn(),
}))

function renderList() {
  return render(
    <MemoryRouter>
      <CategoryList />
    </MemoryRouter>,
  )
}

describe('CategoryList', () => {
  afterEach(() => {
    vi.clearAllMocks()
  })

  it('shows a loading message while categories load', () => {
    getCategories.mockReturnValue(new Promise(() => {}))
    renderList()
    expect(screen.getByText(/loading categories/i)).toBeInTheDocument()
  })

  it('shows each category as a link to its results', async () => {
    getCategories.mockResolvedValue([
      { id: 1, name: 'Food', slug: 'food' },
      { id: 2, name: 'Mental Health', slug: 'mental-health' },
    ])
    renderList()

    expect(await screen.findByRole('link', { name: 'Food' })).toHaveAttribute(
      'href',
      '/results?category=food',
    )
    expect(screen.getByRole('link', { name: 'Mental Health' })).toHaveAttribute(
      'href',
      '/results?category=mental-health',
    )
    expect(getCategories).toHaveBeenCalledTimes(1)
  })

  it('shows an error message when categories fail to load', async () => {
    getCategories.mockRejectedValue(new Error('Request failed: 500'))
    renderList()
    expect(await screen.findByRole('alert')).toHaveTextContent(/could not load categories/i)
  })
})
