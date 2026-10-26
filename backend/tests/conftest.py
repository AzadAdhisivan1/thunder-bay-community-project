"""Shared test fixtures.

Tests run against an in-memory SQLite database, so they don't need Docker or PostgreSQL.
Anything PostGIS-specific (Sprint 2) will need its own integration tests.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app import models
from app.db import Base, get_db
from app.main import app


@pytest.fixture
def db_session():
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    Base.metadata.create_all(engine)
    session = sessionmaker(bind=engine)()
    yield session
    session.close()
    engine.dispose()


@pytest.fixture
def client(db_session):
    app.dependency_overrides[get_db] = lambda: db_session
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture
def make_service(db_session: Session):
    """Create a service (and its category if needed). Usage: make_service(name="Food Bank")."""

    def _make(name="Test Service", category="Food", **fields) -> models.Service:
        slug = category.lower().replace(" ", "-")
        cat = db_session.query(models.Category).filter_by(slug=slug).first()
        if cat is None:
            cat = models.Category(name=category, slug=slug)
            db_session.add(cat)
        defaults = {
            "address": "123 Example St, Thunder Bay, ON",
            "latitude": 48.3809,
            "longitude": -89.2477,
        }
        service = models.Service(name=name, category=cat, **{**defaults, **fields})
        db_session.add(service)
        db_session.commit()
        return service

    return _make
