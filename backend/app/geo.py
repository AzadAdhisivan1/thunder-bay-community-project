"""Location helpers for US-06 (use my location for distance)."""

from dataclasses import dataclass
from math import asin, cos, radians, sin, sqrt

# Mean Earth radius. PostGIS measures on the WGS 84 spheroid instead, so the two
# can differ by up to about 0.5%, which is far below what the UI shows (0.1 km).
EARTH_RADIUS_KM = 6371.0088


@dataclass(frozen=True)
class GeoPoint:
    """A WGS 84 position, e.g. the user's location from the browser."""

    lat: float
    lng: float


def haversine_km(a: GeoPoint, b: GeoPoint) -> float:
    """Great-circle distance between two points in kilometres."""
    dlat = radians(b.lat - a.lat)
    dlng = radians(b.lng - a.lng)
    h = sin(dlat / 2) ** 2 + cos(radians(a.lat)) * cos(radians(b.lat)) * sin(dlng / 2) ** 2
    return 2 * EARTH_RADIUS_KM * asin(min(1.0, sqrt(h)))
