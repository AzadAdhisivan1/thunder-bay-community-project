"""Load Thunder Bay service listings from seed/data/services.csv (US-01).

Owners: Dhara (collect and check the data), Azad (script).
Run with:  docker compose exec backend python -m seed.seed

Acceptance criteria from P1:
  - After a fresh start, at least 50 services are in the database.
  - Every service has a name, category, address, latitude/longitude and last_updated.
  - Running the script a second time does not create duplicates.

The CSV is the source of truth. A service is matched by name + address (the same
pair the database keeps unique). New rows are added, rows whose details changed in
the CSV are updated, and unchanged rows are left alone, so the script is safe to run
again after editing the CSV. Coordinates must already be in the CSV; the seed never
calls Nominatim (that's seed/geocode.py).
"""

import csv
from dataclasses import dataclass
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import SessionLocal
from app.models import Category, Service

DATA_FILE = Path(__file__).parent / "data" / "services.csv"

REQUIRED_FIELDS = ("name", "category", "address", "latitude", "longitude")
OPTIONAL_FIELDS = ("description", "hours", "phone", "website", "eligibility")


@dataclass
class SeedResult:
    categories_created: int = 0
    services_created: int = 0
    services_updated: int = 0
    services_unchanged: int = 0

    def __str__(self) -> str:
        return (
            f"categories created: {self.categories_created}, "
            f"services created: {self.services_created}, "
            f"updated: {self.services_updated}, "
            f"unchanged: {self.services_unchanged}"
        )


def slugify(name: str) -> str:
    """'Mental Health' -> 'mental-health'."""
    return "-".join(name.lower().split())


def read_rows(path: Path) -> list[dict]:
    """Read and check the CSV. Raises ValueError naming the line of any bad row."""
    with path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        missing_columns = [c for c in REQUIRED_FIELDS + OPTIONAL_FIELDS if c not in (reader.fieldnames or [])]
        if missing_columns:
            raise ValueError(f"{path.name} is missing columns: {', '.join(missing_columns)}")

        rows = []
        # Line 1 is the header, so data starts on line 2.
        for line, raw in enumerate(reader, start=2):
            row = {key: (value or "").strip() for key, value in raw.items() if key}
            empty = [field for field in REQUIRED_FIELDS if not row[field]]
            if empty:
                raise ValueError(f"{path.name} line {line}: missing {', '.join(empty)}")
            try:
                row["latitude"] = float(row["latitude"])
                row["longitude"] = float(row["longitude"])
            except ValueError:
                raise ValueError(f"{path.name} line {line}: latitude/longitude must be numbers") from None
            for field in OPTIONAL_FIELDS:
                row[field] = row[field] or None
            rows.append(row)
    return rows


def seed(db: Session, path: Path = DATA_FILE) -> SeedResult:
    """Add or update every service in the CSV. Safe to run more than once."""
    rows = read_rows(path)
    result = SeedResult()

    categories = {c.slug: c for c in db.scalars(select(Category))}
    for row in rows:
        slug = slugify(row["category"])
        if slug not in categories:
            categories[slug] = Category(name=row["category"], slug=slug)
            db.add(categories[slug])
            result.categories_created += 1

    db.flush()  # give new categories their ids

    existing = {(s.name, s.address): s for s in db.scalars(select(Service))}
    for row in rows:
        fields = {
            "category": categories[slugify(row["category"])],
            "latitude": row["latitude"],
            "longitude": row["longitude"],
            **{field: row[field] for field in OPTIONAL_FIELDS},
        }
        service = existing.get((row["name"], row["address"]))
        if service is None:
            service = Service(name=row["name"], address=row["address"], **fields)
            db.add(service)
            existing[(row["name"], row["address"])] = service
            result.services_created += 1
            continue

        changed = False
        for field, value in fields.items():
            if getattr(service, field) != value:
                setattr(service, field, value)
                changed = True
        if changed:
            result.services_updated += 1  # last_updated is refreshed by the model
        else:
            result.services_unchanged += 1

    db.commit()
    return result


def run(path: Path = DATA_FILE) -> SeedResult:
    """Seed the database configured in DATABASE_URL."""
    with SessionLocal() as db:
        return seed(db, path)


if __name__ == "__main__":
    print(f"Seeding from {DATA_FILE.name} ...")
    print(run())
