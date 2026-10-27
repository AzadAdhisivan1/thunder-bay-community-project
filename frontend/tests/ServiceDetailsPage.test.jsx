import { render, screen } from '@testing-library/react'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import ServiceDetailsPage from '../src/pages/ServiceDetailsPage.jsx'
import { getService } from '../src/api/client.js'

vi.mock('../src/api/client.js', () => ({
  getService: vi.fn(),
}))

const fullService = {
  id: 1,
  name: 'Regional Food Distribution Association',
  category: { id: 1, name: 'Food', slug: 'food' },
  description: 'Food bank and emergency food hampers.',
  address: '570 Squier St, Thunder Bay, ON',
  latitude: 48.4071,
  longitude: -89.2537,
  hours: 'Mon-Fri 9:00-16:00',
  phone: '807-555-0100',
  website: 'https://example.org',
  eligibility: 'Open to everyone',
  last_updated: '2026-10-26T12:00:00Z',
}

function renderAt(id) {
  return render(
    <MemoryRouter initialEntries={[`/services/${id}`]}>
      <Routes>
        <Route path="/services/:id" element={<ServiceDetailsPage />} />
      </Routes>
    </MemoryRouter>,
  )
}

// Finds the value shown next to a field label, e.g. "Hours".
function valueOf(label) {
  return screen.getByText(label, { selector: 'dt' }).nextElementSibling
}

describe('ServiceDetailsPage', () => {
  afterEach(() => {
    vi.clearAllMocks()
  })

  it('loads the service with the id from the URL', async () => {
    getService.mockResolvedValue(fullService)
    renderAt(1)
    expect(screen.getByText(/loading service/i)).toBeInTheDocument()
    expect(await screen.findByRole('heading', { name: fullService.name })).toBeInTheDocument()
    expect(getService).toHaveBeenCalledWith('1')
  })

  it('shows every field of the service', async () => {
    getService.mockResolvedValue(fullService)
    renderAt(1)
    await screen.findByRole('heading', { name: fullService.name })

    expect(valueOf('Category')).toHaveTextContent('Food')
    expect(valueOf('Address')).toHaveTextContent('570 Squier St, Thunder Bay, ON')
    expect(valueOf('Hours')).toHaveTextContent('Mon-Fri 9:00-16:00')
    expect(valueOf('Phone')).toHaveTextContent('807-555-0100')
    expect(valueOf('Eligibility')).toHaveTextContent('Open to everyone')
    expect(screen.getByRole('link', { name: 'https://example.org' })).toHaveAttribute(
      'href',
      'https://example.org',
    )
  })

  it('shows "Not available" for missing fields', async () => {
    getService.mockResolvedValue({
      ...fullService,
      hours: null,
      phone: '',
      website: null,
      eligibility: '   ',
    })
    renderAt(1)
    await screen.findByRole('heading', { name: fullService.name })

    expect(valueOf('Hours')).toHaveTextContent('Not available')
    expect(valueOf('Phone')).toHaveTextContent('Not available')
    expect(valueOf('Website')).toHaveTextContent('Not available')
    expect(valueOf('Eligibility')).toHaveTextContent('Not available')
    expect(valueOf('Address')).toHaveTextContent('570 Squier St, Thunder Bay, ON')
  })

  it('does not turn a non-web website value into a link', async () => {
    getService.mockResolvedValue({ ...fullService, website: 'javascript:alert(1)' })
    renderAt(1)
    await screen.findByRole('heading', { name: fullService.name })
    expect(screen.queryByRole('link', { name: /javascript/i })).not.toBeInTheDocument()
  })

  it('shows "Service not found" when the service does not exist', async () => {
    getService.mockRejectedValue(Object.assign(new Error('Request failed: 404'), { status: 404 }))
    renderAt(999)
    expect(await screen.findByRole('heading', { name: 'Service not found' })).toBeInTheDocument()
  })

  it('shows a general error for other failures', async () => {
    getService.mockRejectedValue(Object.assign(new Error('Request failed: 500'), { status: 500 }))
    renderAt(1)
    expect(await screen.findByRole('heading', { name: /something went wrong/i })).toBeInTheDocument()
    expect(screen.queryByText('Service not found')).not.toBeInTheDocument()
  })
})
