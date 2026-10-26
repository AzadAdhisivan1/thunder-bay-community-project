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

// US-02
export function getCategories() {
  return request('/categories')
}

// US-02
export function getServicesByCategory(slug) {
  return request(`/services?category=${encodeURIComponent(slug)}`)
}

// US-03
export function searchServices(query) {
  return request(`/search?q=${encodeURIComponent(query)}`)
}

// US-04. Throws an error with status 404 when the service doesn't exist.
export function getService(id) {
  return request(`/services/${encodeURIComponent(id)}`)
}
