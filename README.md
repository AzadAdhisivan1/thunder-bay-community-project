# Thunder Link: Thunder Bay Smart Community Services Locator

COMP 3415 Software Engineering, Lakehead University

Thunder Link helps people in Thunder Bay find community services (food banks, shelters, health care, recycling, employment support) from one place. Users can browse by category, search by keyword or in plain language, and see results on a map with distances.

| Member | Email | Main area |
|---|---|---|
| Azad Adhisivan | aadhisi1@lakeheadu.ca | Setup, Docker, CI, database, architecture |
| Dhara Satishbhai Patel | dpate303@lakeheadu.ca | Service data, map |
| Santhosh Sai Allada | sallada1@lakeheadu.ca | Backend API, backend tests |
| Kamakshi Borgohain | kborgoh1@lakeheadu.ca | Frontend pages, frontend tests |

---

## Who is doing what: Sprint 2 (P3)

**Sprint goal:** reach about 50% of the backlog with **US-06** (location and distance), **US-07** (plain-language search) and **US-08** (ranked results). That's 21 points, taking us from 18/73 to 39/73. The TA checks working, tested features in the lab, so every story needs tests and must run with `docker compose up`.

Same workflow as Sprint 1: one branch per task, a PR into `main`, CI green, and **one approval from a teammate** before merging. Commit from one GitHub account only.

### Azad: US-06 backend ✅ done
- [x] PostGIS `location` column on `services` (generated from lat/lng) with a GiST index: migration `0002`
- [x] `lat`, `lng`, `max_km` on `/api/services`, `/api/search`, `/api/services/{id}`; `distance_km` on every service; nearest first
- [x] `api/client.js`: every call takes an optional `{ lat, lng, maxKm }` as its last argument
- [x] 40 distance tests (SQLite) + 8 PostGIS tests; CI now starts a PostGIS database
- [x] Contract in [`docs/api.md`](docs/api.md#location-us-06), design in [`docs/architecture.md`](docs/architecture.md#sprint-2-changes-p3)
- [ ] P3 report PDF ([`docs/reports/p3/`](docs/reports/p3/)): each of you, send me your status and test counts when your PR is merged

**Your files:** `backend/app/crud/distance.py`, `backend/app/geo.py`, `backend/app/routers/location.py`, `backend/alembic/`, `backend/tests/test_distance.py`, `backend/tests/test_postgis.py`, `frontend/src/api/client.js`, `.github/`, `docs/architecture.md`, `docs/reports/`

### Dhara: US-06 frontend (location UI)
The backend is ready: try `http://localhost:8000/api/services?lat=48.3809&lng=-89.2477` after pulling `main` and running `docker compose up -d --build`.
- [ ] "Use my location" button on the results page: `navigator.geolocation.getCurrentPosition`
- [ ] Pass the position to the API: `searchServices(q, { lat, lng })`, `getServicesByCategory(slug, { lat, lng })`, `getService(id, { lat, lng })`
- [ ] Show `distance_km` on each `ServiceCard` and on the details page, e.g. "2.9 km away" (one decimal)
- [ ] "You are here" marker on `ResultsMap`, included when the map fits its bounds
- [ ] Location denied or unavailable: show a short message and keep the normal (name-ordered) results
- [ ] Optional: a radius choice (2 / 5 / 10 km) sent as `maxKm`
- [ ] Vitest tests: mock `navigator.geolocation` (success and denied) and the API client
- [ ] Update [`docs/backlog.md`](docs/backlog.md) statuses as stories finish (US-01 to US-05 are Done)

**Acceptance criteria (US-06):** with location allowed, every result shows its distance and the list is nearest first; with location denied, results still show (without distances) and the user sees why; the map shows the user's position. *(Check the exact wording against P1.)*

**Your files:** `frontend/src/components/ResultsMap.jsx`, a new `frontend/src/components/LocationButton.jsx` (or a `useLocation` hook), `docs/backlog.md`. Coordinate with Kamakshi before editing `ServiceCard.jsx` or the pages.

### Santhosh: US-07 plain-language search (timeboxed)
- [ ] `backend/app/nlp/parser.py`: turn a sentence into `{category, keywords}`. Start simple: a keyword → category map (e.g. "hungry", "meal", "groceries" → Food; "bed", "sleep" → Shelter) plus stop-word removal. No ML needed for Sprint 2.
- [ ] `GET /api/search/smart?q=<sentence>` (also accepts `lat`, `lng`): parse, then run the normal search with the extracted words, filtered to the detected category
- [ ] **Fallback (NFR-04):** if parsing finds nothing or raises an error, return the plain keyword search results for the original text. Never return a 500
- [ ] Response includes what was understood, so the UI can say "Showing Food services for: tonight, meal"
- [ ] pytest: example sentences per category, fallback on gibberish, fallback when the parser raises, works with a location
- [ ] Update [`docs/api.md`](docs/api.md) and [`docs/testing-plan.md`](docs/testing-plan.md) (add the Sprint 2 tests)

**Acceptance criteria (US-07):** "I need food tonight" returns Food services; a sentence the parser can't understand still returns keyword results; search never fails because of the NLP step. *(Check against P1.)*

**Your files:** `backend/app/nlp/`, `backend/app/routers/search.py`, `backend/tests/test_nlp.py`, `docs/api.md`, `docs/testing-plan.md`. Reuse `search_query()` in `crud/search.py` and `with_distance()` in `crud/distance.py`.

### Kamakshi: US-08 ranked results + plain-language search UI
- [ ] `backend/app/nlp/ranking.py`: score each result, e.g. name match > category match > description match, minus a small amount per km when a location is given. Pure function with unit tests
- [ ] Use the ranking for `/api/search` and `/api/search/smart` results (agree the hook-in point with Santhosh)
- [ ] Frontend: a "Sort by: Best match / Nearest" choice on the results page (Nearest only when location is on)
- [ ] Frontend: show the "understood as" line from US-07 above the results
- [ ] Tests for the ranking function (pytest) and the sort control (Vitest)

**Acceptance criteria (US-08):** for "food bank", services named "Food Bank" come before ones that only mention it in the description; with a location, of two equally good matches the nearer one comes first. *(Check against P1.)*

**Your files:** `backend/app/nlp/ranking.py`, `backend/tests/test_ranking.py`, `frontend/src/pages/ResultsPage.jsx`, `frontend/src/components/`, `frontend/tests/`

### Everyone
- [ ] Review at least one teammate's PR each week (approve only after running it)
- [ ] Run the PostGIS tests before opening a backend PR (see [Running the tests](#running-the-tests))
- [ ] Be ready to demo your own story and explain its acceptance criteria and tests to the TA

### Order of work
1. **Now:** pull `main`. US-06 backend and the API client are merged, so Dhara can start right away. Santhosh starts the parser; Kamakshi starts the ranking function (pure Python, needs nothing else).
2. **Middle:** Santhosh and Kamakshi agree how ranking plugs into `/api/search/smart`; Dhara's location feeds both.
3. **End:** connect everything, check it in the browser on a phone-width window, send Azad your status for the P3 PDF.

---

## Who is doing what: Sprint 1 (P2)

Sprint goal (from P1 §7): `docker compose up` gives a working site with real Thunder Bay data where you can browse by category, search by keyword, see results on a map and open a details page. CI runs the tests on every pull request.

Tick a box in your PR when your task is done.

### Azad
- [x] Repo skeleton, Docker Compose (FastAPI + React/Vite + PostgreSQL/PostGIS)
- [x] GitHub Actions CI running pytest and Vitest on every PR
- [x] PR template, contributing guide
- [ ] Branch protection on `main` (1 approval + CI must pass)
- [x] Database schema for services and categories (US-01), shared with Dhara
- [x] Seed script `backend/seed/seed.py` that loads the CSV without duplicates (US-01), shared with Dhara
- [x] **Report:** architecture diagram and design notes in `docs/architecture.md` (P2.2)

**Your files:** `docker-compose.yml`, `.github/`, `backend/app/models/`, `backend/alembic/`, `backend/seed/seed.py`, `docs/architecture.md`

### Dhara
- [x] Collect around 50 checked Thunder Bay services into `backend/seed/data/services.csv` (US-01)
- [x] Geocode each address once with Nominatim and save lat/lng in the CSV (don't geocode on every run)
- [x] Leaflet map with OSM tiles, one marker per result, popup with name and link to details (US-05)
- [x] Tests for the map component
- [x] **Report:** updated product backlog in `docs/backlog.md` (P2.5)

**Your files:** `backend/seed/data/`, `backend/seed/geocode.py`, `frontend/src/components/ResultsMap.jsx`, `docs/backlog.md`

### Santhosh
- [x] `GET /api/categories`: only categories that have services (US-02)
- [x] `GET /api/services?category=<slug>` (US-02)
- [x] `GET /api/search?q=<text>`: matches name, category and description (US-03)
- [x] `GET /api/services/{id}` with 404 "Service not found" (US-04 API)
- [x] pytest tests for every endpoint, including the P1 acceptance criteria for US-03
- [x] **Report:** testing plan and test results in `docs/testing-plan.md` (P2.3)

**Your files:** `backend/app/routers/`, `backend/app/crud/`, `backend/tests/`, `docs/testing-plan.md`

### Kamakshi
- [x] Home page category list that links to results (US-02)
- [x] Search bar: empty input isn't sent, shows a "no results" message with a link to categories (US-03)
- [x] Results page list using `ServiceCard` (US-02, US-03)
- [x] Service details page: "Not available" for missing fields, "Service not found" for removed ones (US-04)
- [x] Vitest tests for the pages and components
- [ ] **Report:** implementation summary (report §2)

**Your files:** `frontend/src/pages/`, `frontend/src/components/` (except `ResultsMap.jsx`), `frontend/tests/`

### Everyone
- [ ] Review at least one PR from someone else each week
- [ ] Iteration review in `docs/iteration-reviews/sprint-1.md` (P2.6), filled in together at the end of the sprint
- [ ] Be ready to demo and explain your own part to the TA

### Order of work
1. **Days 1–3:** Azad's skeleton is merged (this PR). Dhara starts the CSV. Santhosh and Kamakshi build against the contract in [`docs/api.md`](docs/api.md); Kamakshi can use fake data until the endpoints land.
2. **Days 4–10:** Feature PRs: seed script, endpoints, pages, map.
3. **Days 11–14:** Connect everything end to end, fix bugs, write the docs and the report.

The full backlog is in [`docs/backlog.md`](docs/backlog.md).

---

## Running the app

You need [Docker Desktop](https://www.docker.com/products/docker-desktop/) running.

```bash
docker compose up --build
```

- Website: http://localhost:5173
- API and interactive docs: http://localhost:8000/docs
- Health check: http://localhost:8000/api/health

Load the 50 Thunder Bay services into the database (run this once after the first start, and again whenever `services.csv` changes):

```bash
docker compose exec backend python -m seed.seed
```

It's safe to run more than once: new services are added, changed ones are updated, and nothing is duplicated. It prints what it did, e.g. `categories created: 10, services created: 50, updated: 0, unchanged: 0`.

The coordinates are already saved in `services.csv`. After adding new services to the CSV, fill in their coordinates once with:

```bash
docker compose exec backend python -m seed.geocode
```

Stop everything with `Ctrl+C`, or `docker compose down`. Add `-v` to also wipe the database.

## Running the tests

With the app running in Docker:

```bash
docker compose exec backend pytest --cov=app
docker compose exec frontend npm test
```

The PostGIS tests (`tests/test_postgis.py`) are skipped unless you point them at a database. They use a separate `thunderlink_test` database that they create and rebuild, so your app data is safe:

```bash
docker compose exec -e TEST_DATABASE_URL=postgresql+psycopg://thunderlink:thunderlink@db:5432/thunderlink_test backend pytest
```

CI always runs them.

Without Docker, you need Python 3.12 and Node 20:

```bash
cd backend && pip install -r requirements-dev.txt && pytest
cd frontend && npm install && npm test
```

Backend tests use an in-memory SQLite database, so they don't need PostgreSQL.

## Database changes

The schema is managed by Alembic. Migrations run automatically when the backend container starts. After changing a model in `backend/app/models/`:

```bash
docker compose exec backend alembic revision --autogenerate -m "describe the change"
```

Check the generated file in `backend/alembic/versions/` and commit it with your model change.

---

## How we work

Read [CONTRIBUTING.md](CONTRIBUTING.md) before your first PR. The short version:

1. `git checkout main && git pull`
2. `git checkout -b feature/us-03-search-api`
3. Commit with the story ID: `US-03: add keyword search endpoint`
4. Push and open a PR into `main`. CI must pass and one teammate must approve.

## Project structure

```
backend/                FastAPI REST API
  app/
    main.py             app entry point, mounts the routers
    config.py, db.py    settings and database session
    models/             SQLAlchemy tables (Category, Service)
    schemas/            response shapes returned by the API
    routers/            endpoints: categories, services, search
    crud/               database query functions
    nlp/                plain-language search and ranking (Sprint 2)
  alembic/              database migrations
  seed/                 seed script and services.csv
  tests/                pytest tests
frontend/               React + Vite + Leaflet
  src/
    api/client.js       all calls to the backend
    pages/              Home, Results, Service details
    components/         SearchBar, CategoryList, ServiceCard, ResultsMap
  tests/                Vitest tests
ml/                     classifier training (US-14, later sprint)
docs/                   architecture, API contract, testing plan, backlog, iteration reviews
.github/                CI workflow and PR template
docker-compose.yml      runs db + backend + frontend
```

## Tech stack

Python, FastAPI, SQLAlchemy, Alembic · PostgreSQL with PostGIS · React, Vite, React Router, Leaflet with OpenStreetMap · pytest, Vitest · Docker Compose · GitHub Actions

Planned for later sprints: scikit-learn, sentence-transformers, spaCy (plain-language search, ranking, classification).
