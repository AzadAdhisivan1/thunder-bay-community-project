// Owner: Dhara (US-05).
// Leaflet map (react-leaflet) with OpenStreetMap tiles, centred on Thunder Bay (48.3809, -89.2477).
// One marker per service; the popup shows the name and a link to /services/<id>.
// Markers must update when the `services` prop changes.
// Remember: import 'leaflet/dist/leaflet.css' or the map tiles won't line up.
export default function ResultsMap({ services = [] }) {
  return <div className="results-map">TODO (US-05): map with {services.length} markers</div>
}
