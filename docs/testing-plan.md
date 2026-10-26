# Testing plan (P2.3)

Owner: Santhosh Sai Allada. Sprint 1 backend API: US-02, US-03, US-04.

## Approach

Backend tests use pytest and FastAPI TestClient with an isolated in-memory SQLite database per test. Requests exercise routing, validation, SQLAlchemy queries and response serialization together. Tests create synthetic services rather than depending on the unfinished seed data. The existing frontend tests use Vitest and React Testing Library. GitHub Actions runs both suites and the frontend build on pull requests; branch protection must be configured separately by the repository maintainer.

A separate local smoke check exercised the running Docker API against PostgreSQL/PostGIS, verifying category listing, filtering, mixed-case phrase search, literal wildcard handling, nullable details, blank-input rejection and deletion followed by 404. Its uniquely named synthetic records were removed after the check. This checks the production database dialect in addition to SQLite; it does not verify real-world listing accuracy or PostGIS spatial queries.

## Story → test traceability

All endpoint tests below are in `backend/tests/test_endpoints.py`.

| Story | Requirement | Test |
|---|---|---|
| US-02 | Only categories with services; no repeated categories | `test_categories_exclude_empty_and_do_not_repeat` |
| US-02 | All services or filter by exact category slug | `test_services_list_all_in_name_order`, `test_services_filter_by_category_slug` |
| US-02 | Unknown/empty category gives an empty list | `test_services_unknown_or_empty_category` |
| US-03 | P1 criterion quoted in the original plan: “food bank” matches name, category or description | `test_food_bank_matches_each_search_field` (three cases) |
| US-03 | No matches returns an empty list | `test_search_no_matches` |
| US-03 | Case-insensitive matching and surrounding whitespace | `test_food_bank_matches_each_search_field` |
| US-03 | Partial phrase matches, unique results, stable order | `test_search_matches_partial_phrase_once_and_orders_results` |
| US-03 | Missing/blank API query returns 422 | `test_search_rejects_missing_or_blank_query` |
| US-03 | Search characters remain literal; SQL-like text is not executed | `test_search_metacharacters_are_literal`, `test_search_no_matches` |
| US-04 | Full details and nullable fields conform to the contract | `test_service_details_preserve_full_contract`, `test_service_nullable_fields_remain_null` |
| US-04 | Missing/removed service returns 404 “Service not found” | `test_missing_service_returns_404`, `test_removed_service_returns_404` |
| US-04 | Invalid id returns 422 | `test_invalid_service_id_returns_422` |
| US-02/03 | Empty database returns empty lists | `test_empty_database_returns_empty_lists` |
| US-01 | Database uniqueness constraint rejects duplicate name/address | Existing `test_models.py::test_same_name_and_address_is_rejected` |

The uniqueness test does **not** demonstrate seed-script idempotency. That test remains with US-01's owner when seeding is implemented. The frontend requirement “empty search box sends no request” remains with Kamakshi; server-side blank-query rejection is covered here. The full P1 document is not in this repository, so traceability uses the criteria recorded in the README, API contract and original testing plan.

## Reproduce

Start Docker Desktop, then run from the repository root:

```bash
docker compose up -d --build
docker compose exec -T backend pytest --cov=app --cov-report=term-missing
docker compose exec -T frontend npm test
docker compose exec -T frontend npm run build
```

Explore the API at http://localhost:8000/docs. Without seeded data, list/search endpoints correctly return `[]`.

## Local results — 2026-10-26

- Backend: **32 passed** (29 endpoint cases plus the 3 existing tests).
- Backend application statement coverage: **97%** (148/152 statements). All CRUD and router statements are covered. Four uncovered statements are the real database session lifecycle, replaced by the isolated test fixture.
- Frontend: **4 passed** across 2 files.
- Frontend production build: **passed**.
- Live PostgreSQL-backed API smoke check: **passed**, including removal of demonstration records.
- Non-blocking warnings: upstream Starlette/AnyIO deprecation and React Router v7 future flags.

These are local results, not claimed CI results. The PR's GitHub Actions checks provide the CI result. Real service data, seed idempotency and frontend interaction acceptance tests remain outside this backend change.
