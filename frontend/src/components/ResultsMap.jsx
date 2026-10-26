// Owner: Dhara (US-05).
// Leaflet map (react-leaflet) with OpenStreetMap tiles, centred on Thunder Bay.
// One marker per service; the popup shows the name and a link to /services/<id>.
import { useEffect } from 'react'
import { Link } from 'react-router-dom'
import { MapContainer, Marker, Popup, TileLayer, useMap } from 'react-leaflet'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import markerIcon from 'leaflet/dist/images/marker-icon.png'
import markerIcon2x from 'leaflet/dist/images/marker-icon-2x.png'
import markerShadow from 'leaflet/dist/images/marker-shadow.png'

export const THUNDER_BAY_CENTER = [48.3809, -89.2477]
const DEFAULT_ZOOM = 12

// Vite renames Leaflet's marker images, so point the default icon at the bundled files.
L.Icon.Default.mergeOptions({
  iconUrl: markerIcon,
  iconRetinaUrl: markerIcon2x,
  shadowUrl: markerShadow,
})

function hasCoordinates(service) {
  return Number.isFinite(service?.latitude) && Number.isFinite(service?.longitude)
}

// Moves the map so every marker is visible whenever the results change.
function FitToMarkers({ positions }) {
  const map = useMap()
  const key = JSON.stringify(positions)

  useEffect(() => {
    if (positions.length === 0) {
      map.setView(THUNDER_BAY_CENTER, DEFAULT_ZOOM)
    } else if (positions.length === 1) {
      map.setView(positions[0], 15)
    } else {
      map.fitBounds(positions, { padding: [30, 30] })
    }
    // `key` changes only when the positions change, not on every render.
  }, [map, key])

  return null
}

export default function ResultsMap({ services = [] }) {
  const mappable = services.filter(hasCoordinates)
  const positions = mappable.map((service) => [service.latitude, service.longitude])

  return (
    <div className="results-map" aria-label="Map of results">
      <MapContainer
        center={THUNDER_BAY_CENTER}
        zoom={DEFAULT_ZOOM}
        scrollWheelZoom={false}
        style={{ height: '400px', width: '100%' }}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        {mappable.map((service) => (
          <Marker key={service.id} position={[service.latitude, service.longitude]}>
            <Popup>
              <strong>{service.name}</strong>
              <br />
              <Link to={`/services/${service.id}`}>View details</Link>
            </Popup>
          </Marker>
        ))}
        <FitToMarkers positions={positions} />
      </MapContainer>
    </div>
  )
}
