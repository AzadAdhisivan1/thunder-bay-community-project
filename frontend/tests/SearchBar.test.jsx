import { fireEvent, render, screen } from '@testing-library/react'
import { MemoryRouter, Route, Routes, useLocation } from 'react-router-dom'
import SearchBar from '../src/components/SearchBar.jsx'
import { searchServices } from '../src/api/client.js'

vi.mock('../src/api/client.js', () => ({
  searchServices: vi.fn(),
}))

// Shows where the search bar sent us, so the test can check the URL.
function CurrentLocation() {
  const location = useLocation()
  return <p data-testid="location">{location.pathname + location.search}</p>
}

function renderSearchBar() {
  return render(
    <MemoryRouter initialEntries={['/']}>
      <Routes>
        <Route path="/" element={<SearchBar />} />
        <Route path="/results" element={<CurrentLocation />} />
      </Routes>
    </MemoryRouter>,
  )
}

function search(text) {
  fireEvent.change(screen.getByLabelText(/search for a service/i), { target: { value: text } })
  fireEvent.click(screen.getByRole('button', { name: 'Search' }))
}

describe('SearchBar', () => {
  afterEach(() => {
    vi.clearAllMocks()
  })

  it('has a labelled text box and a search button', () => {
    renderSearchBar()
    expect(screen.getByLabelText(/search for a service/i)).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Search' })).toBeInTheDocument()
  })

  it('does not search when the input is empty', () => {
    renderSearchBar()
    search('')
    expect(screen.getByRole('alert')).toHaveTextContent('Please type something to search')
    expect(screen.queryByTestId('location')).not.toBeInTheDocument()
    expect(searchServices).not.toHaveBeenCalled()
  })

  it('does not search when the input is only spaces', () => {
    renderSearchBar()
    search('    ')
    expect(screen.getByRole('alert')).toHaveTextContent('Please type something to search')
    expect(screen.queryByTestId('location')).not.toBeInTheDocument()
    expect(searchServices).not.toHaveBeenCalled()
  })

  it('goes to the results page with the trimmed search text', () => {
    renderSearchBar()
    search('  food bank  ')
    expect(screen.getByTestId('location')).toHaveTextContent('/results?q=food%20bank')
  })
})
