"""Load Thunder Bay service listings from seed/data/services.csv (US-01).

Owners: Dhara (collect and check the data), Azad (script).
Run with:  docker compose exec backend python -m seed.seed

Acceptance criteria from P1:
  - After a fresh start, at least 50 services are in the database.
  - Every service has a name, category, address, latitude/longitude and last_updated.
  - Running the script a second time does not create duplicates
    (the services table has a unique constraint on name + address).
"""

from pathlib import Path

DATA_FILE = Path(__file__).parent / "data" / "services.csv"


def run() -> None:
    # TODO (US-01): read DATA_FILE, create missing categories, insert services that aren't there yet.
    raise NotImplementedError("Seed script not written yet (US-01)")


if __name__ == "__main__":
    run()
