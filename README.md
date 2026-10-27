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
