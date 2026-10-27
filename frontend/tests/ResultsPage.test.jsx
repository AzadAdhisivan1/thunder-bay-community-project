import { fireEvent, render, screen, within } from '@testing-library/react'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import ResultsPage from '../src/pages/ResultsPage.jsx'
import { getServicesByCategory, searchServices } from '../src/api/client.js'

vi.mock('../src/api/client.js', () => ({
  getServicesByCategory: vi.fn(),
  searchServices: vi.fn(),
}))

// Leaflet doesn't run in jsdom, so replace the map with a stub that shows what it was given.
vi.mock('../src/components/ResultsMap.jsx', () => ({
  default: ({ services }) => (
    <div data-testid="results-map">{services.map((s) => s.name).join(', ')}</div>
  ),
}))

const services = [
  {
    id: 1,
    name: 'Regional Food Distribution Association',
    category: { id: 1, name: 'Food', slug: 'food' },
    address: '570 Squier St, Thunder Bay, ON',
  },
  {
    id: 2,
    name: 'Dew Drop Inn',
    category: { id: 1, name: 'Food', slug: 'food' },
    address: '101 Simpson St, Thunder Bay, ON',
  },
]

function renderAt(url) {
  return render(
    <MemoryRouter initialEntries={[url]}>
      <Routes>
        <Route path="/results" element={<ResultsPage />} />
      </Routes>
    </MemoryRouter>,
  )
}

describe('ResultsPage', () => {
  afterEach(() => {
    vi.clearAllMocks()
  })

  it('shows a loading message while results load', () => {
    searchServices.mockReturnValue(new Promise(() => {}))
    renderAt('/results?q=food')
    expect(screen.getByText(/loading results/i)).toBeInTheDocument()
  })

  it('shows category results as cards and on the map', async () => {
    getServicesByCategory.mockResolvedValue(services)
    renderAt('/results?category=food')

    const list = await screen.findByRole('list', { name: /results list/i })
    expect(within(list).getAllByRole('article')).toHaveLength(2)
    expect(within(list).getByText('Dew Drop Inn')).toBeInTheDocument()
    expect(getServicesByCategory).toHaveBeenCalledWith('food')
    expect(searchServices).not.toHaveBeenCalled()
    expect(screen.getByTestId('results-map')).toHaveTextContent(
      'Regional Food Distribution Association, Dew Drop Inn',
    )
    expect(screen.getByRole('heading', { level: 1 })).toHaveTextContent('Category: Food')
  })

  it('searches with the text from the URL and shows it in the heading', async () => {
    searchServices.mockResolvedValue([services[0]])
    renderAt('/results?q=food%20bank')

    expect(await screen.findByText('Regional Food Distribution Association', { selector: 'h3' }))
      .toBeInTheDocument()
    expect(searchServices).toHaveBeenCalledWith('food bank')
    expect(getServicesByCategory).not.toHaveBeenCalled()
    expect(screen.getByRole('heading', { level: 1 })).toHaveTextContent('Results for "food bank"')
  })

  it('shows "No results found" with a link back to the categories', async () => {
    searchServices.mockResolvedValue([])
    renderAt('/results?q=zzzz')

    expect(await screen.findByText(/no results found/i)).toBeInTheDocument()
    expect(screen.getByRole('link', { name: /browse the categories/i })).toHaveAttribute(
      'href',
      '/#categories',
    )
    expect(screen.queryByRole('article')).not.toBeInTheDocument()
  })

  it('shows an error message when results fail to load', async () => {
    getServicesByCategory.mockRejectedValue(new Error('Request failed: 500'))
    renderAt('/results?category=food')
    expect(await screen.findByRole('alert')).toHaveTextContent(/could not load results/i)
  })

  it('loads new results when the URL changes', async () => {
    searchServices.mockResolvedValueOnce([services[0]]).mockResolvedValueOnce([services[1]])
    renderAt('/results?q=food')
    expect(await screen.findByText('Regional Food Distribution Association', { selector: 'h3' }))
      .toBeInTheDocument()

    fireEvent.change(screen.getByLabelText(/search for a service/i), {
      target: { value: 'dew drop' },
    })
    fireEvent.click(screen.getByRole('button', { name: 'Search' }))

    expect(await screen.findByText('Dew Drop Inn', { selector: 'h3' })).toBeInTheDocument()
    expect(searchServices).toHaveBeenLastCalledWith('dew drop')
    expect(screen.getByRole('heading', { level: 1 })).toHaveTextContent('Results for "dew drop"')
  })

  it('does not call the API when the URL has no search or category', () => {
    renderAt('/results')
    expect(screen.getByText(/browse the categories/i)).toBeInTheDocument()
    expect(searchServices).not.toHaveBeenCalled()
    expect(getServicesByCategory).not.toHaveBeenCalled()
  })
})
