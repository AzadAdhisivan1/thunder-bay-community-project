"""US-06: use my location for distance (API, on SQLite).

Acceptance criteria (Sprint 2):
  1. With a location, every result has distance_km and the list is nearest first.
  2. Without a location everything works as in Sprint 1 and distance_km is null,
     so the site still works when the user denies location access.
  3. max_km leaves out services further away than the radius.
  4. Distances work with category filtering, keyword search and the details page.
  5. Bad or incomplete locations are rejected with 422, never silently ignored.

The same behaviour on real PostgreSQL + PostGIS is checked in test_postgis.py.
"""

import pytest

from app.geo import GeoPoint, haversine_km

# Thunder Bay City Hall, used as "my location" throughout.
HOME = {"lat": 48.3809, "lng": -89.2477}


@pytest.fixture
def three_services(make_service):
    """Services roughly 0, 1.1 and 11.1 km north of HOME (0.01° latitude ≈ 1.11 km)."""
    far = make_service(name="Alpha Far", category="Food", latitude=48.4809, longitude=-89.2477)
    here = make_service(name="Zulu Here", category="Food", latitude=48.3809, longitude=-89.2477)
    near = make_service(name="Mid Near", category="Health", latitude=48.3909, longitude=-89.2477)
    return far, here, near


# --- the distance formula ---

def test_haversine_zero_for_the_same_point():
    assert haversine_km(GeoPoint(48.38, -89.25), GeoPoint(48.38, -89.25)) == 0


def test_haversine_matches_a_known_distance():
    # One degree of latitude is about 111.2 km anywhere on Earth.
    assert haversine_km(GeoPoint(48.0, -89.0), GeoPoint(49.0, -89.0)) == pytest.approx(111.2, abs=0.1)
    # A quarter of the way around the equator is exactly pi/2 Earth radii.
    assert haversine_km(GeoPoint(0, 0), GeoPoint(0, 90)) == pytest.approx(10007.5, abs=0.1)
    # Order doesn't matter.
    a, b = GeoPoint(48.38, -89.25), GeoPoint(48.43, -89.22)
    assert haversine_km(a, b) == pytest.approx(haversine_km(b, a))


# --- criterion 1: distance on every result, nearest first ---

def test_services_with_location_are_nearest_first(client, three_services):
    data = client.get("/api/services", params=HOME).json()
    assert [s["name"] for s in data] == ["Zulu Here", "Mid Near", "Alpha Far"]
    assert [s["distance_km"] for s in data] == pytest.approx([0.0, 1.11, 11.12], abs=0.01)


def test_distance_is_rounded_to_two_decimals(client, three_services):
    for service in client.get("/api/services", params=HOME).json():
        assert service["distance_km"] == round(service["distance_km"], 2)


def test_equal_distances_keep_name_order(client, make_service):
    make_service(name="Bravo", latitude=48.39, longitude=-89.25)
    make_service(name="Alpha", latitude=48.39, longitude=-89.25)
    data = client.get("/api/services", params=HOME).json()
    assert [s["name"] for s in data] == ["Alpha", "Bravo"]


# --- criterion 2: no location behaves exactly like Sprint 1 ---

@pytest.mark.parametrize("url", ["/api/services", "/api/search?q=r"])
def test_without_location_order_is_by_name_and_distance_is_null(client, three_services, url):
    data = client.get(url).json()
    assert [s["name"] for s in data] == ["Alpha Far", "Mid Near", "Zulu Here"]
    assert all(s["distance_km"] is None for s in data)


# --- criterion 3: radius ---

def test_max_km_leaves_out_services_beyond_the_radius(client, three_services):
    data = client.get("/api/services", params={**HOME, "max_km": 5}).json()
    assert [s["name"] for s in data] == ["Zulu Here", "Mid Near"]


def test_max_km_includes_a_service_exactly_on_the_edge(client, make_service):
    make_service(name="Edge", latitude=48.3909, longitude=-89.2477)  # about 1.112 km
    edge_km = haversine_km(GeoPoint(**HOME), GeoPoint(48.3909, -89.2477))
    assert len(client.get("/api/services", params={**HOME, "max_km": edge_km}).json()) == 1


def test_max_km_with_nothing_in_range_returns_empty_list(client, three_services):
    data = client.get("/api/services", params={"lat": 43.65, "lng": -79.38, "max_km": 10}).json()
    assert data == []


# --- criterion 4: works with the Sprint 1 features ---

def test_category_filter_with_location(client, three_services):
    data = client.get("/api/services", params={**HOME, "category": "food"}).json()
    assert [s["name"] for s in data] == ["Zulu Here", "Alpha Far"]
    assert all(s["category"]["slug"] == "food" for s in data)


def test_search_with_location_is_nearest_first(client, make_service):
    make_service(name="Far Food Bank", latitude=48.4809, longitude=-89.2477)
    make_service(name="Near Food Bank", latitude=48.3819, longitude=-89.2477)
    make_service(name="Near Shelter", category="Shelter", latitude=48.3809, longitude=-89.2477)
    data = client.get("/api/search", params={"q": "food bank", **HOME}).json()
    assert [s["name"] for s in data] == ["Near Food Bank", "Far Food Bank"]
    assert data[0]["distance_km"] == pytest.approx(0.11, abs=0.01)


def test_search_with_radius(client, make_service):
    make_service(name="Far Food Bank", latitude=48.4809, longitude=-89.2477)
    make_service(name="Near Food Bank", latitude=48.3819, longitude=-89.2477)
    data = client.get("/api/search", params={"q": "food bank", **HOME, "max_km": 2}).json()
    assert [s["name"] for s in data] == ["Near Food Bank"]


def test_details_with_location_include_distance(client, three_services):
    far = three_services[0]
    data = client.get(f"/api/services/{far.id}", params=HOME).json()
    assert data["name"] == "Alpha Far"
    assert data["distance_km"] == pytest.approx(11.12, abs=0.01)


def test_details_ignore_radius_so_the_page_still_opens(client, three_services):
    far = three_services[0]
    response = client.get(f"/api/services/{far.id}", params={**HOME, "max_km": 1})
    assert response.status_code == 200


def test_details_with_location_for_missing_service_is_404(client):
    response = client.get("/api/services/999", params=HOME)
    assert response.status_code == 404
    assert response.json() == {"detail": "Service not found"}


# --- criterion 5: bad input is rejected ---

@pytest.mark.parametrize("params", [
    {"lat": 48.38},                              # lng missing
    {"lng": -89.25},                             # lat missing
    {"lat": 91, "lng": -89.25},                  # latitude out of range
    {"lat": 48.38, "lng": -181},                 # longitude out of range
    {"lat": "north", "lng": -89.25},             # not a number
    {"max_km": 5},                               # radius without a location
    {"lat": 48.38, "lng": -89.25, "max_km": 0},  # radius must be positive
    {"lat": 48.38, "lng": -89.25, "max_km": 101},  # radius over the 100 km cap
])
@pytest.mark.parametrize("url", ["/api/services", "/api/search?q=food", "/api/services/1"])
def test_bad_location_is_rejected(client, make_service, url, params):
    make_service()
    assert client.get(url, params=params).status_code == 422
