"""US-06 on real PostgreSQL + PostGIS: the migration and the distance queries.

The unit tests use SQLite, which has no PostGIS, so these run only when
TEST_DATABASE_URL points at a PostgreSQL server (CI sets it; locally see README):

    docker compose exec -e TEST_DATABASE_URL=postgresql+psycopg://thunderlink:thunderlink@db:5432/thunderlink_test backend pytest tests/test_postgis.py

The test database is created if needed and rebuilt from the migrations, so the real
app database is never touched.
"""

import os
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url
from sqlalchemy.orm import sessionmaker

from app.config import settings
from app.db import get_db
from app.geo import GeoPoint, haversine_km
from app.main import app
from app.models import Category, Service

TEST_URL = os.environ.get("TEST_DATABASE_URL")
pytestmark = pytest.mark.skipif(not TEST_URL, reason="TEST_DATABASE_URL not set (needs PostgreSQL + PostGIS)")

BACKEND = Path(__file__).resolve().parents[1]
HOME = GeoPoint(48.3809, -89.2477)  # Thunder Bay City Hall


def _alembic(url: str, monkeypatch) -> Config:
    # alembic/env.py reads the URL from app settings, so point those at the test database.
    monkeypatch.setattr(settings, "database_url", url)
    config = Config(str(BACKEND / "alembic.ini"))
    config.set_main_option("script_location", str(BACKEND / "alembic"))
    return config


@pytest.fixture(scope="module")
def pg_engine():
    url = make_url(TEST_URL)
    admin = create_engine(url.set(database="postgres"), isolation_level="AUTOCOMMIT")
    with admin.connect() as conn:
        exists = conn.scalar(text("SELECT 1 FROM pg_database WHERE datname = :n"), {"n": url.database})
        if not exists:
            conn.execute(text(f'CREATE DATABASE "{url.database}"'))
    admin.dispose()

    mp = pytest.MonkeyPatch()
    config = _alembic(TEST_URL, mp)
    command.downgrade(config, "base")
    command.upgrade(config, "head")
    mp.undo()

    engine = create_engine(TEST_URL)
    yield engine
    engine.dispose()


@pytest.fixture
def pg(pg_engine):
    session = sessionmaker(bind=pg_engine)()
    yield session
    session.rollback()
    session.execute(text("TRUNCATE services, categories RESTART IDENTITY CASCADE"))
    session.commit()
    session.close()


@pytest.fixture
def pg_client(pg):
    app.dependency_overrides[get_db] = lambda: pg
    yield TestClient(app)
    app.dependency_overrides.clear()


def add(pg, name, lat, lng, category="Food"):
    slug = category.lower()
    cat = pg.query(Category).filter_by(slug=slug).first() or Category(name=category, slug=slug)
    service = Service(name=name, category=cat, address=f"{name} St", latitude=lat, longitude=lng)
    pg.add(service)
    pg.commit()
    return service


# --- migration 0002 ---

def test_location_column_is_generated_from_coordinates(pg):
    service = add(pg, "City Hall", HOME.lat, HOME.lng)
    lng, lat = pg.execute(
        text("SELECT ST_X(location::geometry), ST_Y(location::geometry) FROM services WHERE id = :i"),
        {"i": service.id},
    ).one()
    assert (lat, lng) == pytest.approx((HOME.lat, HOME.lng))


def test_location_follows_when_coordinates_change(pg):
    service = add(pg, "Moving", HOME.lat, HOME.lng)
    service.latitude = 48.4809
    pg.commit()
    lat = pg.scalar(text("SELECT ST_Y(location::geometry) FROM services WHERE id = :i"), {"i": service.id})
    assert lat == pytest.approx(48.4809)


def test_location_has_a_gist_index(pg):
    indexdef = pg.scalar(text("SELECT indexdef FROM pg_indexes WHERE indexname = 'ix_services_location'"))
    assert indexdef and "gist" in indexdef.lower()


def test_migration_downgrades_and_upgrades_cleanly(pg_engine, monkeypatch):
    config = _alembic(TEST_URL, monkeypatch)
    command.downgrade(config, "0001")
    with pg_engine.connect() as conn:
        assert conn.scalar(text(
            "SELECT count(*) FROM information_schema.columns "
            "WHERE table_name = 'services' AND column_name = 'location'"
        )) == 0
    command.upgrade(config, "head")


# --- distance queries through the API ---

def test_distances_match_haversine_and_are_nearest_first(pg, pg_client):
    add(pg, "Far", 48.4809, -89.2477)
    add(pg, "Here", 48.3809, -89.2477)
    add(pg, "Downtown", 48.4280, -89.2160)
    data = pg_client.get("/api/services", params={"lat": HOME.lat, "lng": HOME.lng}).json()
    assert [s["name"] for s in data] == ["Here", "Downtown", "Far"]
    for s in data:
        expected = haversine_km(HOME, GeoPoint(s["latitude"], s["longitude"]))
        # PostGIS measures on the spheroid; allow 0.5% (+ rounding) difference from the sphere.
        assert s["distance_km"] == pytest.approx(expected, rel=0.005, abs=0.01)


def test_radius_uses_postgis(pg, pg_client):
    add(pg, "Far", 48.4809, -89.2477)
    add(pg, "Near", 48.3909, -89.2477)
    data = pg_client.get("/api/services", params={"lat": HOME.lat, "lng": HOME.lng, "max_km": 5}).json()
    assert [s["name"] for s in data] == ["Near"]


def test_search_and_category_with_location(pg, pg_client):
    add(pg, "Far Food Bank", 48.4809, -89.2477)
    add(pg, "Near Food Bank", 48.3819, -89.2477)
    add(pg, "Shelter Here", 48.3809, -89.2477, category="Shelter")
    params = {"lat": HOME.lat, "lng": HOME.lng}
    search = pg_client.get("/api/search", params={"q": "food bank", **params}).json()
    assert [s["name"] for s in search] == ["Near Food Bank", "Far Food Bank"]
    food = pg_client.get("/api/services", params={"category": "food", **params}).json()
    assert [s["name"] for s in food] == ["Near Food Bank", "Far Food Bank"]


def test_details_with_location_on_postgis(pg, pg_client):
    far = add(pg, "Far", 48.4809, -89.2477)
    data = pg_client.get(f"/api/services/{far.id}", params={"lat": HOME.lat, "lng": HOME.lng}).json()
    assert data["distance_km"] == pytest.approx(11.12, rel=0.005)
    missing = pg_client.get("/api/services/999", params={"lat": HOME.lat, "lng": HOME.lng})
    assert missing.status_code == 404
