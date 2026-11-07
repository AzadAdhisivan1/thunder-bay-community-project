# API contract

Base URL: `/api`. The frontend calls these through `frontend/src/api/client.js`. Live docs are at http://localhost:8000/docs once the backend is running.

If you change anything here, update this file in the same PR.

## Service object

Every endpoint that returns services uses this shape:

```json
{
  "id": 1,
  "name": "Regional Food Distribution Association",
  "category": { "id": 1, "name": "Food", "slug": "food" },
  "description": "Food bank and emergency food hampers.",
  "address": "570 Squier St, Thunder Bay, ON",
  "latitude": 48.4071,
  "longitude": -89.2537,
  "hours": "Mon-Fri 9:00-16:00",
  "phone": "807-555-0100",
  "website": "https://example.org",
  "eligibility": "Open to everyone",
  "last_updated": "2026-10-26T12:00:00Z",
  "distance_km": 2.91
}
```

`description`, `hours`, `phone`, `website` and `eligibility` can be `null`. The UI shows "Not available" for these (US-04).

`distance_km` (US-06) is the straight-line distance in kilometres, rounded to 2 decimals, from the location sent with the request. It is `null` when no location was sent.

## Endpoints

| Method | Path | Story | Returns |
|---|---|---|---|
| GET | `/api/health` | – | `{"status": "ok"}` |
| GET | `/api/categories` | US-02 | List of `{id, name, slug}`; only categories with at least one service |
| GET | `/api/services?category=<slug>` | US-02 | List of services in that category (all services if no category) |
| GET | `/api/search?q=<text>` | US-03 | Services whose name, category or description match `q`; `[]` if none |
| GET | `/api/services/{id}` | US-04 | One service, or `404 {"detail": "Service not found"}` |

### Location (US-06)

`/api/services`, `/api/search` and `/api/services/{id}` accept these optional query parameters:

| Parameter | Meaning |
|---|---|
| `lat`, `lng` | The user's position (WGS 84). Must be sent together. `lat` −90 to 90, `lng` −180 to 180 |
| `max_km` | Only services within this many km (more than 0, at most 100). Needs `lat` and `lng`. Ignored by `/api/services/{id}`, so a details page always opens |

With a location, every service has `distance_km` and lists are sorted **nearest first** (ties by name, then id). Without one, the responses are exactly as in Sprint 1.

```
GET /api/search?q=food%20bank&lat=48.3809&lng=-89.2477&max_km=5
```

In the frontend, pass `{ lat, lng, maxKm }` as the last argument of `getServicesByCategory`, `searchServices` or `getService` in `api/client.js`.

### Errors

- `lat` without `lng` (or the reverse), out-of-range values, `max_km` without a location, or `max_km` outside 0–100 → `422`
- Missing, empty, or whitespace-only `q` on `/api/search` → `422`
- Unknown service id → `404 {"detail": "Service not found"}`
- Non-integer service id → `422`

### Matching and ordering

- Categories and services are returned by name, then id for stable ordering. Empty categories are omitted.
- Category filtering uses the exact category slug; an unknown or empty slug returns `[]`.
- Search trims surrounding whitespace and matches a case-insensitive literal substring in the service name, category name, or description. A multiword query such as `food bank` matches that phrase within any one field.
- `%`, `_`, and `/` in search input are literal characters, not SQL wildcards. Null descriptions do not prevent matches in the other fields. A service matching multiple fields appears only once.
