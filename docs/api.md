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
  "last_updated": "2026-10-26T12:00:00Z"
}
```

`description`, `hours`, `phone`, `website` and `eligibility` can be `null`. The UI shows "Not available" for these (US-04).

## Endpoints

| Method | Path | Story | Returns |
|---|---|---|---|
| GET | `/api/health` | – | `{"status": "ok"}` |
| GET | `/api/categories` | US-02 | List of `{id, name, slug}`; only categories with at least one service |
| GET | `/api/services?category=<slug>` | US-02 | List of services in that category (all services if no category) |
| GET | `/api/search?q=<text>` | US-03 | Services whose name, category or description match `q`; `[]` if none |
| GET | `/api/services/{id}` | US-04 | One service, or `404 {"detail": "Service not found"}` |

### Errors

- Empty `q` on `/api/search` → `422`
- Unknown service id → `404 {"detail": "Service not found"}`
- Endpoint not written yet → `501`
