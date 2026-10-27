"""US-01: the seed script loads services.csv and is safe to run again. Owner: Azad."""

import csv
import time

import pytest

from app.models import Category, Service
from seed.seed import DATA_FILE, read_rows, seed, slugify

HEADER = [
    "name", "category", "description", "address", "latitude", "longitude",
    "hours", "phone", "website", "eligibility",
]


def write_csv(path, rows):
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=HEADER)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in HEADER})
    return path


def row(**fields):
    defaults = {
        "name": "Test Food Bank", "category": "Food", "address": "1 Test St, Thunder Bay, ON",
        "latitude": "48.40", "longitude": "-89.24",
    }
    return {**defaults, **fields}


# --- P1 acceptance criteria, against the real data file ---

def test_fresh_seed_loads_at_least_50_services(db_session):
    result = seed(db_session)
    assert db_session.query(Service).count() >= 50
    assert result.services_created == db_session.query(Service).count()


def test_every_seeded_service_has_the_required_fields(db_session):
    seed(db_session)
    for service in db_session.query(Service):
        assert service.name and service.address
        assert service.category is not None
        assert service.latitude is not None and service.longitude is not None
        assert service.last_updated is not None


def test_running_the_seed_twice_creates_no_duplicates(db_session):
    seed(db_session)
    services = db_session.query(Service).count()
    categories = db_session.query(Category).count()

    second = seed(db_session)

    assert db_session.query(Service).count() == services
    assert db_session.query(Category).count() == categories
    assert second.services_created == 0
    assert second.categories_created == 0
    assert second.services_unchanged == services


def test_seeded_data_is_served_by_the_api(client, db_session):
    seed(db_session)
    categories = client.get("/api/categories").json()
    assert {c["slug"] for c in categories} >= {"food", "shelter", "health"}
    food = client.get("/api/services", params={"category": "food"}).json()
    assert food and all(s["category"]["slug"] == "food" for s in food)


# --- behaviour on small test files ---

def test_categories_are_created_once_with_url_slugs(db_session, tmp_path):
    path = write_csv(tmp_path / "s.csv", [
        row(name="A", category="Mental Health"),
        row(name="B", category="Mental Health", address="2 Test St"),
    ])
    result = seed(db_session, path)
    assert result.categories_created == 1
    assert db_session.query(Category).one().slug == "mental-health"


def test_empty_optional_fields_are_stored_as_null(db_session, tmp_path):
    seed(db_session, write_csv(tmp_path / "s.csv", [row()]))
    service = db_session.query(Service).one()
    for field in ("description", "hours", "phone", "website", "eligibility"):
        assert getattr(service, field) is None


def test_changed_rows_are_updated_and_last_updated_moves(db_session, tmp_path):
    path = tmp_path / "s.csv"
    seed(db_session, write_csv(path, [row(hours="Mon 9-5")]))
    before = db_session.query(Service).one().last_updated

    time.sleep(1.1)  # SQLite timestamps have one-second resolution
    result = seed(db_session, write_csv(path, [row(hours="Mon-Fri 9-5")]))

    service = db_session.query(Service).one()
    assert result.services_updated == 1
    assert service.hours == "Mon-Fri 9-5"
    assert service.last_updated > before


def test_existing_categories_are_reused(db_session, tmp_path):
    db_session.add(Category(name="Food", slug="food"))
    db_session.commit()
    result = seed(db_session, write_csv(tmp_path / "s.csv", [row()]))
    assert result.categories_created == 0
    assert db_session.query(Category).count() == 1


@pytest.mark.parametrize("field", ["name", "category", "address", "latitude", "longitude"])
def test_missing_required_field_names_the_line(tmp_path, field):
    second = row(name="Second", address="2 Test St")
    second[field] = ""
    path = write_csv(tmp_path / "s.csv", [row(), second])
    with pytest.raises(ValueError, match=f"line 3: missing {field}"):
        read_rows(path)


def test_non_numeric_coordinates_are_rejected(tmp_path):
    path = write_csv(tmp_path / "s.csv", [row(latitude="north")])
    with pytest.raises(ValueError, match="line 2: latitude/longitude must be numbers"):
        read_rows(path)


def test_bad_file_changes_nothing_in_the_database(db_session, tmp_path):
    with pytest.raises(ValueError):
        seed(db_session, write_csv(tmp_path / "s.csv", [row(), row(name="")]))
    assert db_session.query(Service).count() == 0


def test_missing_column_is_reported(tmp_path):
    path = tmp_path / "s.csv"
    path.write_text("name,category,address\nA,Food,1 Test St\n", encoding="utf-8")
    with pytest.raises(ValueError, match="missing columns"):
        read_rows(path)


def test_slugify():
    assert slugify("Food") == "food"
    assert slugify("  Mental   Health ") == "mental-health"


def test_real_data_file_is_the_default():
    assert DATA_FILE.name == "services.csv"
    assert len(read_rows(DATA_FILE)) >= 50
