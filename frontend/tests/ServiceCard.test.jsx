import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import ServiceCard from '../src/components/ServiceCard.jsx'

const service = {
  id: 7,
  name: 'Shelter House',
  category: { id: 2, name: 'Shelter', slug: 'shelter' },
  address: '420 George St, Thunder Bay, ON',
}

describe('ServiceCard', () => {
  it('shows the name, category and address', () => {
    render(
      <MemoryRouter>
        <ServiceCard service={service} />
      </MemoryRouter>,
    )
    expect(screen.getByRole('heading', { name: 'Shelter House' })).toBeInTheDocument()
    expect(screen.getByText('Shelter')).toBeInTheDocument()
    expect(screen.getByText('420 George St, Thunder Bay, ON')).toBeInTheDocument()
  })

  it('links to the service details page', () => {
    render(
      <MemoryRouter>
        <ServiceCard service={service} />
      </MemoryRouter>,
    )
    expect(screen.getByRole('link', { name: /view details/i })).toHaveAttribute(
      'href',
      '/services/7',
    )
  })
})
