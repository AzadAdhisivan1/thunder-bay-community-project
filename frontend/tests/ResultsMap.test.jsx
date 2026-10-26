import { render, screen, within } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import ResultsMap, { THUNDER_BAY_CENTER } from '../src/components/ResultsMap.jsx'

// Leaflet needs a real browser to draw tiles, so swap react-leaflet for simple
// stand-ins that render their props. This tests our component, not Leaflet.
const mapStub = { setView: vi.fn(), fitBounds: vi.fn() }

vi.mock('react-leaflet', () => ({
  MapContainer: ({ center, children }) => (
    <div data-testid="map" data-center={center.join(',')}>
      {children}
    </div>
  ),
  TileLayer: ({ url }) => <div data-testid="tiles" data-url={url} />,
  Marker: ({ position, children }) => (
    <div data-testid="marker" data-position={position.join(',')}>
      {children}
    </div>
  ),
  Popup: ({ children }) => <div data-testid="popup">{children}</div>,
  useMap: () => mapStub,
}))

const services = [
  { id: 1, name: 'Regional Food Distribution Association', latitude: 48.4071, longitude: -89.2537 },
  { id: 2, name: 'Shelter House', latitude: 48.3822, longitude: -89.2461 },
]

function renderMap(props) {
  return render(
    <MemoryRouter>
      <ResultsMap {...props} />
    </MemoryRouter>,
  )
}

describe('ResultsMap', () => {
  beforeEach(() => {
    mapStub.setView.mockClear()
    mapStub.fitBounds.mockClear()
  })

  it('is centred on Thunder Bay with OpenStreetMap tiles', () => {
    renderMap({ services: [] })
    expect(screen.getByTestId('map')).toHaveAttribute('data-center', THUNDER_BAY_CENTER.join(','))
    expect(screen.getByTestId('tiles').getAttribute('data-url')).toContain('tile.openstreetmap.org')
  })

  it('shows one marker per service at its coordinates', () => {
    renderMap({ services })
    const markers = screen.getAllByTestId('marker')
    expect(markers).toHaveLength(2)
    expect(markers[0]).toHaveAttribute('data-position', '48.4071,-89.2537')
    expect(markers[1]).toHaveAttribute('data-position', '48.3822,-89.2461')
  })

  it('shows the name and a link to the details page in each popup', () => {
    renderMap({ services })
    const popup = screen.getAllByTestId('popup')[1]
    expect(within(popup).getByText('Shelter House')).toBeInTheDocument()
    expect(within(popup).getByRole('link', { name: /view details/i })).toHaveAttribute(
      'href',
      '/services/2',
    )
  })

  it('shows no markers when there are no results', () => {
    renderMap({ services: [] })
    expect(screen.queryAllByTestId('marker')).toHaveLength(0)
    expect(mapStub.setView).toHaveBeenCalledWith(THUNDER_BAY_CENTER, 12)
  })

  it('skips services that have no coordinates', () => {
    renderMap({ services: [...services, { id: 3, name: 'No location', latitude: null, longitude: null }] })
    expect(screen.getAllByTestId('marker')).toHaveLength(2)
    expect(screen.queryByText('No location')).not.toBeInTheDocument()
  })

  it('updates the markers and the view when the results change', () => {
    const { rerender } = renderMap({ services })
    expect(mapStub.fitBounds).toHaveBeenCalledTimes(1)

    rerender(
      <MemoryRouter>
        <ResultsMap services={[services[0]]} />
      </MemoryRouter>,
    )
    expect(screen.getAllByTestId('marker')).toHaveLength(1)
    expect(screen.queryByText('Shelter House')).not.toBeInTheDocument()
    expect(mapStub.setView).toHaveBeenLastCalledWith([48.4071, -89.2537], 15)
  })
})
