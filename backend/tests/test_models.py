"""US-01: the database stores every field a listing needs and blocks duplicates."""

import pytest
from sqlalchemy.exc import IntegrityError

from app import models


def test_service_has_required_fields(make_service):
    service = make_service(name="Regional Food Distribution", category="Food")

    assert service.id is not None
    assert service.category.name == "Food"
    assert service.address
    assert service.latitude and service.longitude
    assert service.last_updated is not None


def test_same_name_and_address_is_rejected(make_service, db_session):
    make_service(name="Shelter House", category="Shelter")

    with pytest.raises(IntegrityError):
        make_service(name="Shelter House", category="Shelter")
    db_session.rollback()

    assert db_session.query(models.Service).count() == 1
