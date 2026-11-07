import { afterEach, describe, expect, it, vi } from 'vitest'
import { getService, getServicesByCategory, searchServices } from '../src/api/client.js'

function mockFetch(status, body) {
  globalThis.fetch = vi.fn().mockResolvedValue({
    ok: status >= 200 && status < 300,
    status,
    json: () => Promise.resolve(body),
  })
}

afterEach(() => {
  vi.restoreAllMocks()
})

describe('api client', () => {
  it('encodes the search text in the URL', async () => {
    mockFetch(200, [])
    await searchServices('food bank')
    expect(fetch).toHaveBeenCalledWith('/api/search?q=food%20bank')
  })

  it('throws with status 404 when a service is missing', async () => {
    mockFetch(404, { detail: 'Service not found' })
    await expect(getService(999)).rejects.toMatchObject({ status: 404 })
  })
})

describe('api client with a location (US-06)', () => {
  const near = { lat: 48.3809, lng: -89.2477 }

  it('leaves the URLs unchanged without a location', async () => {
    mockFetch(200, [])
    await getServicesByCategory('food')
    await getService(3)
    expect(fetch).toHaveBeenNthCalledWith(1, '/api/services?category=food')
    expect(fetch).toHaveBeenNthCalledWith(2, '/api/services/3')
  })

  it('adds lat and lng to category results', async () => {
    mockFetch(200, [])
    await getServicesByCategory('food', near)
    expect(fetch).toHaveBeenCalledWith('/api/services?category=food&lat=48.3809&lng=-89.2477')
  })

  it('adds lat, lng and max_km to a search', async () => {
    mockFetch(200, [])
    await searchServices('food bank', { ...near, maxKm: 5 })
    expect(fetch).toHaveBeenCalledWith('/api/search?q=food%20bank&lat=48.3809&lng=-89.2477&max_km=5')
  })

  it('adds lat and lng to the details request', async () => {
    mockFetch(200, {})
    await getService(3, near)
    expect(fetch).toHaveBeenCalledWith('/api/services/3?lat=48.3809&lng=-89.2477')
  })
})
