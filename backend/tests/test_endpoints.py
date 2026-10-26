"""Sprint 1 API acceptance and regression tests (US-02, US-03, US-04)."""

import pytest

from app.models import Category


def test_categories_exclude_empty_and_do_not_repeat(client, db_session, make_service):
    db_session.add(Category(name="Empty", slug="empty"))
    make_service(name="Zulu", category="Shelter")
    make_service(name="Alpha", category="Food")
    make_service(name="Beta", category="Food")
    response = client.get("/api/categories")
    assert response.status_code == 200
    assert [item["slug"] for item in response.json()] == ["food", "shelter"]
    assert all(set(item) == {"id", "name", "slug"} for item in response.json())


@pytest.mark.parametrize("url", ["/api/categories", "/api/services", "/api/search?q=food"])
def test_empty_database_returns_empty_lists(client, url):
    response = client.get(url)
    assert response.status_code == 200
    assert response.json() == []


def test_services_list_all_in_name_order(client, make_service):
    make_service(name="Zulu", category="Shelter")
    make_service(name="Alpha", category="Food")
    response = client.get("/api/services")
    assert response.status_code == 200
    assert [item["name"] for item in response.json()] == ["Alpha", "Zulu"]


def test_services_filter_by_category_slug(client, make_service):
    expected = make_service(name="Food support", category="Food Support")
    make_service(name="Shelter", category="Housing")
    response = client.get("/api/services", params={"category": "food-support"})
    assert response.status_code == 200
    assert [item["id"] for item in response.json()] == [expected.id]
    assert response.json()[0]["category"]["slug"] == "food-support"


@pytest.mark.parametrize("category", ["unknown", "food", "", "food' OR 1=1 --"])
def test_services_unknown_or_empty_category(client, make_service, category):
    make_service(category="Food Support")
    response = client.get("/api/services", params={"category": category})
    assert response.status_code == 200
    assert response.json() == []


def test_service_details_preserve_full_contract(client, make_service):
    service = make_service(
        name="Test Centre", description="Support services", hours="Monday 9–5",
        phone="807-555-0100", website="https://example.org", eligibility="Everyone",
    )
    response = client.get(f"/api/services/{service.id}")
    assert response.status_code == 200
    data = response.json()
    assert set(data) == {
        "id", "name", "category", "description", "address", "latitude", "longitude",
        "hours", "phone", "website", "eligibility", "last_updated",
    }
    for field in set(data) - {"category", "last_updated"}:
        assert data[field] == getattr(service, field)
    assert data["category"] == {"id": service.category.id, "name": "Food", "slug": "food"}
    assert data["last_updated"]


def test_service_nullable_fields_remain_null(client, make_service):
    service = make_service()
    data = client.get(f"/api/services/{service.id}").json()
    for field in ("description", "hours", "phone", "website", "eligibility"):
        assert data[field] is None


def test_missing_service_returns_404(client):
    response = client.get("/api/services/999999")
    assert response.status_code == 404
    assert response.json() == {"detail": "Service not found"}


def test_removed_service_returns_404(client, db_session, make_service):
    service = make_service()
    service_id = service.id
    db_session.delete(service)
    db_session.commit()
    response = client.get(f"/api/services/{service_id}")
    assert response.status_code == 404
    assert response.json() == {"detail": "Service not found"}


def test_invalid_service_id_returns_422(client):
    assert client.get("/api/services/not-an-id").status_code == 422


@pytest.mark.parametrize("fields", [
    {"name": "Community Food Bank"},
    {"category": "Food Bank"},
    {"description": "Visit our food bank for support"},
])
def test_food_bank_matches_each_search_field(client, make_service, fields):
    expected = make_service(**fields)
    make_service(name="Unrelated clinic", category="Health")
    response = client.get("/api/search", params={"q": "  FoOd BaNk  "})
    assert response.status_code == 200
    assert [item["id"] for item in response.json()] == [expected.id]
    assert response.json()[0]["category"]["name"] == expected.category.name


def test_search_matches_partial_phrase_once_and_orders_results(client, make_service):
    make_service(name="Zulu Food Bank", category="Food Bank", description="food bank")
    make_service(name="Alpha Food Bank", category="Food Bank")
    response = client.get("/api/search", params={"q": "ood ban"})
    assert response.status_code == 200
    assert [item["name"] for item in response.json()] == ["Alpha Food Bank", "Zulu Food Bank"]


@pytest.mark.parametrize("query", ["no such service", "' OR 1=1 --"])
def test_search_no_matches(client, make_service, query):
    make_service()
    response = client.get("/api/search", params={"q": query})
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.parametrize("query", ["%", "_", "/", "50%_/"])
def test_search_metacharacters_are_literal(client, make_service, query):
    expected = make_service(name=f"Literal {query} support")
    make_service(name="Unrelated support")
    response = client.get("/api/search", params={"q": query})
    assert response.status_code == 200
    assert [item["id"] for item in response.json()] == [expected.id]


@pytest.mark.parametrize("query", [None, "", "   ", "\t\n"])
def test_search_rejects_missing_or_blank_query(client, query):
    params = {} if query is None else {"q": query}
    assert client.get("/api/search", params=params).status_code == 422
