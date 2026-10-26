import { afterEach, describe, expect, it, vi } from 'vitest'
import { getService, searchServices } from '../src/api/client.js'

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
