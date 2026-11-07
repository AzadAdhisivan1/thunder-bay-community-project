// Every call to the backend goes through this file. Endpoint shapes are in docs/api.md.

async function request(path) {
  const response = await fetch(`/api${path}`)
  if (!response.ok) {
    const error = new Error(`Request failed: ${response.status}`)
    error.status = response.status
    throw error
  }
  return response.json()
}

// US-06. `near` is optional: { lat, lng } and, if wanted, maxKm.
// With it, each service comes back with distance_km and lists are nearest first.
function locationParams(near) {
  if (!near) return ''
  const params = new URLSearchParams({ lat: String(near.lat), lng: String(near.lng) })
  if (near.maxKm != null) params.set('max_km', String(near.maxKm))
  return `&${params}`
}

// US-02
export function getCategories() {
  return request('/categories')
}

// US-02 (+ US-06 distance)
export function getServicesByCategory(slug, near) {
  return request(`/services?category=${encodeURIComponent(slug)}${locationParams(near)}`)
}

// US-03 (+ US-06 distance)
export function searchServices(query, near) {
  return request(`/search?q=${encodeURIComponent(query)}${locationParams(near)}`)
}

// US-04 (+ US-06 distance). Throws an error with status 404 when the service doesn't exist.
export function getService(id, near) {
  const query = locationParams(near)
  return request(`/services/${encodeURIComponent(id)}${query ? `?${query.slice(1)}` : ''}`)
}
