# Product backlog (P2.5)

Owner: Dhara. Keep this in sync with the GitHub Projects board. Status values: To Do, In Progress, Done, Moved, Cut.

Last updated: end of Sprint 1.

| Order | ID | Story | Priority | Points | Sprint | Owner | Status |
|---|---|---|---|---|---|---|---|
| 1 | US-01 | Load initial service data | Blocker | 5 | 1 | Dhara, Azad | In Progress |
| 2 | US-02 | Browse services by category | Blocker | 3 | 1 | Santhosh (API), Kamakshi (UI) | In Progress |
| 3 | US-03 | Keyword search | Blocker | 3 | 1 | Santhosh (API), Kamakshi (UI) | In Progress |
| 4 | US-04 | View service details | Critical | 2 | 1 | Santhosh (API), Kamakshi (UI) | In Progress |
| 5 | US-05 | See results on a map | Critical | 5 | 1 | Dhara | In Progress |
| 6 | US-06 | Use my location for distance | Critical | 5 | 2 | | To Do |
| 7 | US-07 | Plain language search | Critical | 8 | 2 | | To Do |
| 8 | US-08 | Ranked results | Major | 8 | | | To Do |
| 9 | US-09 | Register and log in | Major | 5 | | | To Do |
| 10 | US-10 | Admin manages listings | Major | 5 | | | To Do |
| 11 | US-12 | Set preferences | Minor | 3 | | | To Do |
| 12 | US-11 | Save favourites | Minor | 3 | | | To Do |
| 13 | US-13 | Personalized recommendations | Minor | 8 | | | To Do |
| 14 | US-14 | ML category suggestion | Minor | 8 | | | To Do |
| 15 | US-15 | Admin manages users | Trivial | 2 | | | To Do |

Total: 73 points. Sprint 1: 18 points.

## Sprint 1 progress

| Story | Done | Left |
|---|---|---|
| US-01 | 50 Thunder Bay services in `backend/seed/data/services.csv`, each with name, category, address and coordinates. Addresses geocoded once with Nominatim (`backend/seed/geocode.py`) and saved in the CSV. Data checks in `backend/tests/test_seed_data.py`. | Seed script `backend/seed/seed.py` that loads the CSV without duplicates (Azad). |
| US-02 | `GET /api/categories` and `GET /api/services?category=` with tests (PR #3). | Home page category list (Kamakshi). |
| US-03 | `GET /api/search?q=` with tests (PR #3). | Search bar and results list (Kamakshi). |
| US-04 | `GET /api/services/{id}` with 404 handling and tests (PR #3). | Details page (Kamakshi). |
| US-05 | `ResultsMap` component: OpenStreetMap tiles centred on Thunder Bay, one marker per result, popup with name and link to `/services/<id>`, markers and view update when results change. Tests in `frontend/tests/ResultsMap.test.jsx`. | Results page must load results and pass them to `<ResultsMap services={...} />` (shared with Kamakshi's results page). |

No Sprint 1 story is fully Done yet, because each one needs both a backend and a frontend part. Every story has its main part finished, and they close when the seed script and pages are merged.

## Changes since P1

- **Jest → Vitest for frontend tests.** Vitest runs with Vite without extra configuration and uses the same test syntax as Jest.
- **Data source for US-01.** Services come from the 211 Ontario North directory (northwesthealthline.ca, run by the Lakehead Social Planning Council) and the City of Thunder Bay website, checked in October 2026. 211 listings already list address, hours, phone and eligibility, so this was faster and more reliable than collecting each one from separate websites.
- **Categories for US-01/US-02.** The data uses 10 categories: Food, Shelter, Health, Mental Health, Employment, Legal, Library, Community, Newcomers, Recycling. P1 named food banks, shelters, health care, recycling and employment; Mental Health, Legal, Library, Community and Newcomers were added because many Thunder Bay services didn't fit the original five.
- **Geocoding is a one-off step, not part of seeding.** `seed/geocode.py` fills only empty coordinates, so Nominatim is called once per address (its usage policy allows 1 request per second). Two addresses that Nominatim matched to the wrong place (Legal Aid at Centennial Square, Lakehead Social Planning Council at Victoriaville Centre) were corrected by hand.
- **Confidential locations left out.** Women's shelters such as Faye Peterson House and Beendigen keep their addresses private, so they are not on the map. Sprint 2 could add phone-only listings for them.
