# Testing plan (P2.3)

Owner: Santhosh. Fill this in as tests are written.

## What we test and how

| Layer | Tool | What | Where |
|---|---|---|---|
| Backend unit/integration | pytest + FastAPI TestClient, in-memory SQLite | Models, every endpoint, error cases | `backend/tests/` |
| Frontend | Vitest + React Testing Library | Pages, components, API client | `frontend/tests/` |
| CI | GitHub Actions | Both suites on every PR; PR can't merge if they fail (NFR-05) | `.github/workflows/ci.yml` |

## Story → test traceability

Show at least one story checked against its P1 acceptance criteria.

| Story | Acceptance criterion (P1) | Test |
|---|---|---|
| US-01 | Running the seed twice doesn't create duplicates | `backend/tests/test_models.py::test_same_name_and_address_is_rejected` |
| US-03 | "food bank" returns services with food bank in name, category or description | TODO |
| US-03 | No matches → empty list | TODO |
| US-03 | Empty search box → nothing sent | TODO (frontend) |
| US-04 | Removed service → "Service not found" | TODO |

## Results

TODO: paste the summary from the latest CI run (pass/fail counts and coverage).
